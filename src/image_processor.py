from PIL import Image, ImageOps


class ImageProcessor:
    """Image processing operations."""
    @staticmethod
    def scale(image: Image.Image, scale_factor: float) -> Image.Image:
        new_size = (int(image.width * scale_factor), int(image.height * scale_factor))
        return image.resize(new_size, Image.Resampling.LANCZOS)

    @staticmethod
    def resize(image: Image.Image, width: int, height: int) -> Image.Image:
        if width <= 0 or height <= 0:
            raise ValueError("Dimensions must be positive integers")
        return image.resize((width, height), Image.Resampling.LANCZOS)

    @staticmethod
    def to_grayscale(image: Image.Image) -> Image.Image:
        return ImageOps.grayscale(image)

    @staticmethod
    def lower_quality(image: Image.Image) -> Image.Image:
        w, h = image.size
        temp = image.resize((max(1, w // 3), max(1, h // 3)), Image.Resampling.LANCZOS)
        return temp.resize((w, h), Image.Resampling.LANCZOS)
