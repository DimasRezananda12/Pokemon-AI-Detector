'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Header() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    if (path === '/') return pathname === '/';
    return pathname?.startsWith(path);
  };

  return (
    <header className="sticky top-0 z-50 bg-dark-surface/80 backdrop-blur-md border-b border-dark-border">
      <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary rounded-md flex items-center justify-center">
            <span className="text-white font-bold text-sm">PA</span>
          </div>
          <Link href="/" className="text-lg font-bold text-white no-underline hover:no-underline">
            PokeAuthAI
          </Link>
        </div>

        {/* Nav */}
        <nav className="hidden md:flex items-center gap-8">
          <Link
            href="/"
            className={`text-sm no-underline transition-colors ${
              isActive('/') && !isActive('/scan')
                ? 'text-white font-semibold'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            Home
          </Link>
          <Link
            href="/scan"
            className={`text-sm no-underline transition-colors ${
              isActive('/scan')
                ? 'text-primary font-bold border-b-2 border-primary pb-1'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            Scan Card
          </Link>
          <Link
            href="/results"
            className={`text-sm no-underline transition-colors ${
              isActive('/results')
                ? 'text-primary font-bold border-b-2 border-primary pb-1'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            My Results
          </Link>
        </nav>

        {/* Sign In */}
        <button className="bg-primary hover:bg-primary-dark text-white font-semibold text-sm px-5 py-2 rounded-md transition-colors">
          Sign In
        </button>
      </div>
    </header>
  );
}
