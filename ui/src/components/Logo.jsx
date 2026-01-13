import React from 'react';
import { handleImageError } from '../utils/imageUtils';
// In a real implementation, you would import the Base64 string here
// import logoBase64 from '../assets/logoBase64';

function Logo() {
  // For now, use the direct path as Base64 integration in React needs a different approach
  // In a real production environment, the Base64 string would be imported or embedded
  return (
    <img 
      src="/Gemini_Generated_Image_kg014vkg014vkg01.png" 
      alt="Nextier Nigeria Violent Conflict Database Logo" 
      className="h-10 w-10 object-contain"
      onError={(e) => handleImageError(e, null)}
    />
  );
}

export default Logo;
