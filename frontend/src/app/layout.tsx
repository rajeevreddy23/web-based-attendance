import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { Sidebar } from "@/components/Sidebar";
import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "SmartAttend - Period-Wise Facial Recognition Attendance System",
  description: "Web-Based Period-Wise Student Attendance Management Using Real-Time Facial Recognition",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 font-sans antialiased min-h-screen">
        <AuthProvider>
          <div className="flex min-h-screen">
            <Sidebar />
            <div className="flex-1 flex flex-col min-w-0">
              <Navbar />
              <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full">
                {children}
              </main>
            </div>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
