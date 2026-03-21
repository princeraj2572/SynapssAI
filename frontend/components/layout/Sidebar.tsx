'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';
import {
  Home,
  Activity,
  BookOpen,
  Heart,
  Smartphone,
  BarChart3,
  Target,
  Brain,
  AlertCircle,
  Settings,
  Lock
} from 'lucide-react';

const NAV = [
  { href: '/',          label: 'Dashboard',    Icon: Home },
  { href: '/activities', label: 'Activities',   Icon: Activity },
  { href: '/journal',    label: 'Journal',      Icon: BookOpen },
  { href: '/analytics',  label: 'Analytics',    Icon: BarChart3 },
  { href: '/digest',     label: 'Digest',       Icon: Brain },
  { href: '/goals',      label: 'Goals',        Icon: Target },
  { href: '/wellness',   label: 'Wellness',     Icon: Heart },
  { href: '/alerts',     label: 'Alerts',       Icon: AlertCircle },
  { href: '/settings',   label: 'Settings',     Icon: Settings },
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
                  <item.Icon size={18} />
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      <div className="px-3 py-3 bg-secondary rounded-lg border border-border mx-1">
        <div className="flex items-center gap-2 text-foreground">
          <Lock size={14} />
          <span className="text-xs font-medium">Private &amp; Secure</span>
        </div>
        <p className="text-xs text-muted-foreground mt-1">All data stays local.</p>
      </div>
    </aside>
  );
}
