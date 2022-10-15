import inspect, torch
from typing import List, Optional, Union
from PIL import Image
from diffusers.schedulers import LMSDiscreteScheduler

# Fork of StableDiffusion __call__ method
def text2img(
		pipeline,
		step_callback,
		prompt: Union[str, List[str]],
		height: Optional[int] = 512,
		width: Optional[int] = 512,
		num_inference_steps: Optional[int] = 50,
		guidance_scale: Optional[float] = 7.5,
		eta: Optional[float] = 0.0,
		generator: Optional[torch.Generator] = None,
		latents: Optional[torch.FloatTensor] = None,
	) -> Image.Image:
		# get prompt text embeddings
		text_input = pipeline.tokenizer(
			prompt,
			padding="max_length",
			max_length=pipeline.tokenizer.model_max_length,
			truncation=True,
			return_tensors="pt",
		)
		text_embeddings = pipeline.text_encoder(text_input.input_ids.to(pipeline.device))[0]

		do_classifier_free_guidance = guidance_scale > 1.0
		if do_classifier_free_guidance:
			max_length = text_input.input_ids.shape[-1]
			uncond_input = pipeline.tokenizer(
				[""], padding="max_length", max_length=max_length, return_tensors="pt"
			)
			uncond_embeddings = pipeline.text_encoder(uncond_input.input_ids.to(pipeline.device))[0]
			text_embeddings = torch.cat([uncond_embeddings, text_embeddings])

		latents_device = "cpu" if pipeline.device.type == "mps" else pipeline.device
		latents_shape = (1, pipeline.unet.in_channels, height // 8, width // 8)
		if latents is None:
			latents = torch.randn(
				latents_shape,
				generator=generator,
				device=latents_device,
			)
		else:
			if latents.shape != latents_shape:
				raise ValueError(f"Unexpected latents shape, got {latents.shape}, expected {latents_shape}")
		latents = latents.to(pipeline.device)

		# set timesteps
		accepts_offset = "offset" in set(inspect.signature(pipeline.scheduler.set_timesteps).parameters.keys())
		extra_set_kwargs = {}
		if accepts_offset:
			extra_set_kwargs["offset"] = 1

		pipeline.scheduler.set_timesteps(num_inference_steps, **extra_set_kwargs)

		# if we use LMSDiscreteScheduler, let's make sure latents are mulitplied by sigmas
		if isinstance(pipeline.scheduler, LMSDiscreteScheduler):
			latents = latents * pipeline.scheduler.sigmas[0]

		accepts_eta = "eta" in set(inspect.signature(pipeline.scheduler.step).parameters.keys())
		extra_step_kwargs = {}
		if accepts_eta:
			extra_step_kwargs["eta"] = eta

		for i, t in enumerate(pipeline.scheduler.timesteps):
			# expand the latents if we are doing classifier free guidance
			latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
			if isinstance(pipeline.scheduler, LMSDiscreteScheduler):
				sigma = pipeline.scheduler.sigmas[i]
				# the model input needs to be scaled to match the continuous ODE formulation in K-LMS
				latent_model_input = latent_model_input / ((sigma**2 + 1) ** 0.5)

			# predict the noise residual
			noise_pred = pipeline.unet(latent_model_input, t, encoder_hidden_states=text_embeddings).sample

			# perform guidance
			if do_classifier_free_guidance:
				noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
				noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)

			# compute the previous noisy sample x_t -> x_t-1
			if isinstance(pipeline.scheduler, LMSDiscreteScheduler):
				latents = pipeline.scheduler.step(noise_pred, i, latents, **extra_step_kwargs).prev_sample
			else:
				latents = pipeline.scheduler.step(noise_pred, t, latents, **extra_step_kwargs).prev_sample

			# call the step callback
			step_callback(i+1, latents)

		# scale and decode the image latents with vae
		latents = 1 / 0.18215 * latents
		image = pipeline.vae.decode(latents).sample

		image = (image / 2 + 0.5).clamp(0, 1)
		image = image.cpu().permute(0, 2, 3, 1).numpy()

		return pipeline.numpy_to_pil(image)[0]
