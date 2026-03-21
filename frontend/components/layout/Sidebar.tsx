'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';

const NAV = [
  { href: '/',          label: 'Dashboard',   icon: '◉' },
  { href: '/activities',    label: 'Activities',     icon: '⌨' },
  { href: '/journal',     label: 'Journal',      icon: '📖' },
  { href: '/wellness',    label: 'Wellness',     icon: '❤' },
  { href: '/collectors',    label: 'Collectors',     icon: '📱' },
  { href: '/scores',      label: 'Scores',       icon: '✦' },
  { href: '/goals', label: 'Goals',  icon: '◈' },
  { href: '/memory',      label: 'Memory',   icon: '✧' },
  { href: '/alerts',    label: 'Alerts',     icon: '◎' },
  { href: '/settings',  label: 'Settings',   icon: '⚙' },
];

export default function Sidebar() {
  const path = usePathname();
  return (
    <aside className="w-64 border-r border-border bg-card flex flex-col py-6 px-3">
      <div className="px-4 mb-8">
        <Link href="/" className="flex items-center gap-3 hover:opacity-75 transition-opacity">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-lg bg-blue-600">
            S
          </div>
          <div>
            <p className="font-bold text-foreground">SynapseAI</p>
            <p className="text-xs text-muted-foreground">Life Analytics</p>
          </div>
        </Link>
      </div>
      <nav className="flex-1">
        <ul className="space-y-1">
          {NAV.map((item) => {
            const isActive = path === item.href;
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={clsx(
                    "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                    isActive
                      ? "bg-blue-600 text-white"
                      : "text-foreground hover:bg-secondary"
                  )}
                >
                  <span className="text-base">{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      <div className="px-3 py-3 bg-secondary rounded-lg border border-border mx-1">
        <p className="text-xs font-medium text-foreground">🔒 Private &amp; Secure</p>
        <p className="text-xs text-muted-foreground mt-1">All data stays local.</p>
      </div>
    </aside>
  );
}
