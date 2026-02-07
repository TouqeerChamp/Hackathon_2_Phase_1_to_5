'use client';

import { useAuth } from '@/context/auth-context';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="border-b bg-white dark:bg-zinc-950">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/dashboard" className="text-xl font-bold">
          Todo App
        </Link>
        <div className="flex items-center gap-4">
          <span className="text-sm text-zinc-500 hidden sm:inline-block">
            {user?.email}
          </span>
          <Button variant="outline" onClick={logout} size="sm">
            Logout
          </Button>
        </div>
      </div>
    </header>
  );
}
