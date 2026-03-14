"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function NavBar() {
  const pathname = usePathname();

  const link = (href: string, label: string) => (
    <Link
      href={href}
      className={`text-sm font-medium transition-colors ${
        pathname === href
          ? "text-td-green"
          : "text-td-muted hover:text-td-dark"
      }`}
    >
      {label}
    </Link>
  );

  return (
    <nav className="border-b border-gray-100 bg-white sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-td-green flex items-center justify-center">
            <span className="text-white text-xs font-bold">TD</span>
          </div>
          <span className="font-semibold text-td-dark text-sm tracking-tight">
            Threat Denied
          </span>
        </Link>
        <div className="flex items-center gap-6">
          {link("/", "Verify")}
          {link("/dashboard", "Dashboard")}
          {link("/profile", "Profile")}
        </div>
      </div>
    </nav>
  );
}
