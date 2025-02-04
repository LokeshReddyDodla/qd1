"use client";
import { useState, useEffect } from "react";
import { Menu, X } from "lucide-react";
import Link from "next/link"; // Import Link from Next.js

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [toggleDropdown, setToggleDropdown] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav
      className={`fixed top-6 left-1/2 transform -translate-x-[43%] z-50 flex justify-center px-8 py-4 transition-all duration-300 ${
        isScrolled
          ? "backdrop-blur-md bg-white/20 shadow-lg rounded-full"
          : "bg-transparent"
      }`}
      style={{ maxWidth: "80%", minWidth: "300px" }}
    >
      {/* Desktop Navigation */}
      <div className="hidden sm:flex text-white space-x-8">
        <Link href="/" passHref>
          <button className="hover:text-gray-300 transition duration-300">HOME</button>
        </Link>
        <Link href="/#about" passHref>
          <button className="hover:text-gray-300 transition duration-300">ABOUT US</button>
        </Link>
        <Link href="/#speakers" passHref>
          <button className="hover:text-gray-300 transition duration-300">SPEAKERS & JUDGES</button>
        </Link>
        <Link href="/sponsors" passHref>
          <button className="hover:text-gray-300 transition duration-300">PARTNERS</button>
        </Link>
        <Link href="/organizers" passHref>
          <button className="hover:text-gray-300 transition duration-300">ORGANIZERS</button>
        </Link>
        <Link href="/timeline" passHref>
          <button className="hover:text-gray-300 transition duration-300">SCHEDULE</button>
        </Link>
      </div>

      {/* Mobile Navigation */}
      <div className="sm:hidden flex flex-col items-end relative">
        <button onClick={() => setToggleDropdown(!toggleDropdown)} className="text-white">
          {toggleDropdown ? <X size={28} /> : <Menu size={28} />}
        </button>

        {toggleDropdown && (
          <div className="absolute top-10 right-0 w-48 backdrop-blur-md bg-white/20 text-white rounded-lg py-3 shadow-lg flex flex-col items-start space-y-3 px-4">
            <Link href="/" passHref>
              <button className="hover:text-gray-300 transition duration-300">HOME</button>
            </Link>
            <Link href="/#about" passHref>
              <button className="hover:text-gray-300 transition duration-300">ABOUT US</button>
            </Link>
            <Link href="/#speakers" passHref>
              <button className="hover:text-gray-300 transition duration-300">SPEAKERS & JUDGES</button>
            </Link>
            <Link href="/sponsors" passHref>
              <button className="hover:text-gray-300 transition duration-300">PARTNERS</button>
            </Link>
            <Link href="/organizors" passHref>
              <button className="hover:text-gray-300 transition duration-300">ORGANIZERS</button>
            </Link>
            <Link href="/timeline" passHref>
              <button className="hover:text-gray-300 transition duration-300">SCHEDULE</button>
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
