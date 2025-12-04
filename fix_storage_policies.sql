-- Fix Storage Policies for student-docs bucket
-- These policies need proper USING and WITH CHECK clauses

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow service_role full access 1xy63rh_0" ON storage.objects;
DROP POLICY IF EXISTS "Allow service_role full access 1xy63rh_1" ON storage.objects;
DROP POLICY IF EXISTS "Allow service_role full access 1xy63rh_2" ON storage.objects;
DROP POLICY IF EXISTS "Allow service_role full access 1xy63rh_3" ON storage.objects;

-- Create a single comprehensive policy for service_role
CREATE POLICY "Allow service_role full access to student-docs"
ON storage.objects
FOR ALL
TO service_role
USING (bucket_id = 'student-docs')
WITH CHECK (bucket_id = 'student-docs');

-- Also allow public read access (since bucket is public)
CREATE POLICY "Allow public read access to student-docs"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'student-docs');

