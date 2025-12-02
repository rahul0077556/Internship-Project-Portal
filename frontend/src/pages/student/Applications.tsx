import React from 'react';
import { useSearchParams } from 'react-router-dom';
import Opportunities from './Opportunities';

const StudentApplications: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  
  React.useEffect(() => {
    // Set the tab to applications if not already set
    if (searchParams.get('tab') !== 'applications') {
      setSearchParams({ tab: 'applications' });
    }
  }, [searchParams, setSearchParams]);

  return <Opportunities />;
};

export default StudentApplications;
