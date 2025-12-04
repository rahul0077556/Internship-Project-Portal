-- Storage Policy for student-docs bucket
-- This allows service_role to upload, read, update, and delete files

-- Policy for INSERT (uploading files)
CREATE POLICY "Allow service_role to upload files"
ON storage.objects
FOR INSERT
TO service_role
WITH CHECK (bucket_id = 'student-docs');

-- Policy for SELECT (reading files)
CREATE POLICY "Allow service_role to read files"
ON storage.objects
FOR SELECT
TO service_role
USING (bucket_id = 'student-docs');

-- Policy for UPDATE (updating files)
CREATE POLICY "Allow service_role to update files"
ON storage.objects
FOR UPDATE
TO service_role
USING (bucket_id = 'student-docs')
WITH CHECK (bucket_id = 'student-docs');

-- Policy for DELETE (deleting files)
CREATE POLICY "Allow service_role to delete files"
ON storage.objects
FOR DELETE
TO service_role
USING (bucket_id = 'student-docs');

-- Also allow public read access (since bucket is public)
CREATE POLICY "Allow public read access"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'student-docs');

