class SigLIPImageEmbedder:
    async def embed_image(self, image_path: str) -> list[float]:
        raise NotImplementedError("Wire SigLIP2 model loading in deployment-specific code.")

