import fs from 'fs';
import path from 'path';
import { glob } from 'glob';

// Function to check if file exists with case sensitivity
const checkFileExistsCaseSensitive = (filePath) => {
  const dir = path.dirname(filePath);
  const fileName = path.basename(filePath);
  try {
    const files = fs.readdirSync(dir);
    return files.includes(fileName);
  } catch (error) {
    console.error(`Error checking file existence for ${filePath}:`, error);
    return false;
  }
};

// Main function to validate asset paths
const validateAssets = () => {
  console.log('Validating asset paths in codebase...');
  let hasError = false;

  // Find all JS/JSX files in src directory
  const files = glob.sync('src/**/*.{js,jsx}');

  files.forEach(file => {
    const content = fs.readFileSync(file, 'utf8');
    const matches = content.match(/src=["']([^"']+)["']/g);

    if (matches) {
      matches.forEach(match => {
        const srcPath = match.replace(/src=["']([^"']+)["']/, '$1');
        if (srcPath.startsWith('/')) {
          const assetPath = path.join('public', srcPath.slice(1));
          if (!checkFileExistsCaseSensitive(assetPath)) {
            console.error(`Asset not found or case mismatch: ${srcPath} in file ${file}`);
            hasError = true;
          }
        }
      });
    }
  });

  if (!hasError) {
    console.log('All asset paths validated successfully.');
  } else {
    process.exit(1);
  }
};

validateAssets();
