'use client';

import { useState, useEffect } from 'react';
import {  PanelRight, PanelLeft,Sun, Moon, BookOpenText, LayoutDashboard, ChartBarDecreasing, Cpu, ChevronLeft, ChevronRight } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import '@/app/globals.css'; 
import { ThemeProvider } from "@/components/theme-provider";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const pathname = usePathname();
  
  useEffect(() => {
  const savedTheme = localStorage.getItem('theme');
  setTimeout(() => {
    if (savedTheme) {
      setIsDark(savedTheme === 'dark');
    } else {
      setIsDark(false);
    }
  }, 0);
}, []);

  useEffect(() => {
  if (isDark) {
    document.documentElement.classList.add('dark');
    localStorage.setItem('theme', 'dark');
  } else {
    document.documentElement.classList.remove('dark');
    localStorage.setItem('theme', 'light');
  }
}, [isDark]); 

  const getLinkClass = (path: string) => {
    const baseClass = "flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-300 group relative ";
    const activeClass = "text-white bg-white/10 shadow-sm";
    const inactiveClass = "text-slate-400 hover:text-white hover:bg-white/10";
    const collapseModifier = isCollapsed ? "justify-center px-0 w-11 h-11 mx-auto" : "";
    
    return `${baseClass} ${pathname === path ? activeClass : inactiveClass} ${collapseModifier}`;
  };

  return (
    <html lang="en" suppressHydrationWarning>
      
      <body className="bg-[#F5F7FA] dark:bg-[#0A0F1C] text-slate-900 dark:text-slate-100 transition-colors">
        <div className="flex min-h-screen">
          <aside 
            className={`bg-gradient-to-b from-[#0F2942] to-[#1A3D5C] text-white p-4 flex flex-col justify-between fixed h-full shadow-lg z-30 transition-all duration-300 ease-in-out ${
              isCollapsed ? 'w-20' : 'w-64'
            }`}
          >
            <button 
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="absolute -right-3 top-7 bg-[#1A3D5C] border border-slate-700 text-white rounded-full p-1 hover:bg-[#24527a] transition-colors shadow-md z-40"
            >
              {isCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
            </button>
            <div>
              <div className={`flex items-center gap-3 mb-8 ${isCollapsed ? 'justify-center mt-2' : 'pl-2'}`}>
                <BookOpenText size={35} className="text-emerald-400 shrink-0" />
                {!isCollapsed && (
                  <div className="transition-all duration-300 opacity-100 whitespace-nowrap">
                    <h1 className="font-bold text-2xl leading-none tracking-tight">XAI HUB</h1>
                    <span className="text-[15px] text-slate-400 block mt-0.5">Sistem Informasi</span>
                  </div>
                )}
              </div>
              <nav className="space-y-2">
                <Link href="/" className={getLinkClass('/')} title="Dashboard">
                  <LayoutDashboard size={20} className="shrink-0" />
                  {!isCollapsed && <span>Dashboard</span>}
                  {isCollapsed && <span className="absolute left-16 bg-[#0F2942] text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity border border-slate-700 whitespace-nowrap z-50 pointer-events-none shadow-md">Dashboard</span>}
                </Link>

                <Link href="/gap-analysis" className={getLinkClass('/gap-analysis')} title="Gap Analysis">
                  <ChartBarDecreasing size={20} className="shrink-0" />
                  {!isCollapsed && <span>Gap Analysis</span>}
                  {isCollapsed && <span className="absolute left-16 bg-[#0F2942] text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity border border-slate-700 whitespace-nowrap z-50 pointer-events-none shadow-md">Gap Analysis</span>}
                </Link>

                <Link href="/explainability" className={getLinkClass('/explainability')} title="Explainability">
                  <Cpu size={20} className="shrink-0" />
                  {!isCollapsed && <span>Explainability</span>}
                  {isCollapsed && <span className="absolute left-16 bg-[#0F2942] text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity border border-slate-700 whitespace-nowrap z-50 pointer-events-none shadow-md">Explainability</span>}
                </Link>
              </nav>
              </div>
            
          <div className="space-y-3">
              {/* User Info */}
              <div className={`flex items-center bg-white/5 rounded-xl transition-all duration-300 ${isCollapsed ? 'p-1 justify-center' : 'p-3 gap-3'}`}>
                <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center text-xs font-bold shrink-0">N</div>
                {!isCollapsed && (
                  <div className="text-xs truncate">
                    <p className="font-semibold text-slate-200">User Mode</p>
                    <p className="text-[10px] text-slate-400">Program Studi</p>
                  </div>
                )}
              </div>
              {/* <button 
                onClick={() => setIsDark(!isDark)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/10 transition-all text-sm font-medium ${isCollapsed ? 'justify-center' : ''}`}
              >
                {isDark ? (
                  <>
                    <Sun size={20} className="text-amber-400" />
                    {!isCollapsed && <span>Light Mode</span>}
                  </>
                ) : (
                  <>
                    <Moon size={20} className="text-slate-300" />
                    {!isCollapsed && <span>Dark Mode</span>}
                  </>
                )}
              </button> */}
              </div> 
            
          </aside>
          <div 
            className={`flex-1 min-h-screen flex flex-col transition-all duration-300 ease-in-out ${
              isCollapsed ? 'ml-20' : 'ml-64'
            }`}
          >
            {children}
          </div>

        </div>
        
      </body>
    </html>
  );
}