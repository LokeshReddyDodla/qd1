import type { Metadata } from "next";
import { Anton,  Poppins } from "next/font/google";
import "./globals.css";
import Navbar from '@/components/selfcomponents/Navbar';
import Footer from '@/components/selfcomponents/Footer';

const anton = Anton({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-anton", // CSS Variable
});

// Load Poppins
const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "700"], // Add multiple weights if needed
  variable: "--font-poppins", // CSS Variable
});

export const metadata: Metadata = {
  title: "Hive  ",
  description: "hackthon for web3 enthusiasts",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${anton.variable} ${poppins.variable}  antialiased`}
      >
        <Navbar/>
        {children}
        <Footer />
      </body>
    </html>
  );
}
