-- Fix photo_url column to support base64 images
-- Run this if you need to manually fix the column without running migrations

-- Change photo_url from VARCHAR(500) to TEXT
ALTER TABLE face_profiles 
ALTER COLUMN photo_url TYPE TEXT;

-- Verify the change
SELECT 
    column_name, 
    data_type, 
    character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'face_profiles' 
AND column_name = 'photo_url';
