'use client';

import { useAuth } from '@/context/auth-context';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { MessageCircle, LayoutDashboard } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function Header() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  const navLinks = [
    {
      href: '/dashboard',
      label: 'Dashboard',
      icon: LayoutDashboard
    },
    {
      href: '/chat',
      label: 'Chat with AI',
      icon: MessageCircle
    }
  ];

  return (
    <header className="border-b border-purple-100 bg-white/90 backdrop-blur-sm">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo and Nav */}
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="text-xl font-bold text-purple-700">
            Todo App
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-purple-100 text-purple-700'
                      : 'text-gray-600 hover:bg-purple-50 hover:text-purple-600'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {link.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* User Info and Logout */}
        <div className="flex items-center gap-4">
          {/* Mobile Nav */}
          <div className="flex md:hidden items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    'p-2 rounded-lg transition-colors',
                    isActive
                      ? 'bg-purple-100 text-purple-700'
                      : 'text-gray-600 hover:bg-purple-50 hover:text-purple-600'
                  )}
                  aria-label={link.label}
                >
                  <Icon className="h-5 w-5" />
                </Link>
              );
            })}
          </div>

          <span className="text-sm text-gray-500 hidden sm:inline-block">
            {user?.email}
          </span>
          <Button
            variant="outline"
            onClick={logout}
            size="sm"
            className="border-purple-200 text-purple-600 hover:bg-purple-50"
          >
            Logout
          </Button>
        </div>
      </div>
    </header>
  );
}
