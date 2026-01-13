export const handleImageError = (event, fallbackSrc) => {
  console.error('Image failed to load:', event.target.src);
  if (fallbackSrc) {
    event.target.src = fallbackSrc;
  }
};
