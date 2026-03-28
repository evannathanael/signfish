import Link from 'next/link';

const nav = [
  { href: '/', label: 'Dashboard' },
  { href: '/leaderboard', label: 'Leaderboard' },
  { href: '/settings', label: 'Settings' },
  { href: '/login', label: 'Login' }
];

export default function Layout({ children }) {
  return (
    <div className="mx-auto min-h-screen w-full max-w-6xl px-4 py-6">
      <header className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">TinyFish AI</p>
          <h1 className="text-2xl font-black">SignFish Type Race</h1>
        </div>
        <nav className="flex flex-wrap gap-3 text-sm">
          {nav.map((item) => (
            <Link key={item.href} href={item.href}>
              {item.label}
            </Link>
          ))}
        </nav>
      </header>
      {children}
    </div>
  );
}
