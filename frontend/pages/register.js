import { useEffect } from 'react';
import { useRouter } from 'next/router';

export default function RegisterPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/login?mode=register');
  }, [router]);

  return null;
}
