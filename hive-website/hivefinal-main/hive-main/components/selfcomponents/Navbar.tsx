"use client"
import { useState, useEffect } from 'react';
import Link from 'next/link';
// import { Home, Info, Users, Award, Building2, Calendar } from 'lucide-react';

const Navbar = () => {
  // const [activeItem, setActiveItem] = React.useState('home');
  const [toggleDropdown, setToggleDropdown] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 0) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`flex min-w-screen font-poppins py-4 px-6 justify-between fixed w-full top-0 z-50 transition-all duration-300 ${
      isScrolled ? 'bg-black/70 backdrop-blur-sm' : 'bg-transparent'
    }`}>
      
      <div>
      <Link href="/" className='text-2xl font-bold text-white'>HIVE</Link>
      </div>
{/* desktop */}
      <div className='sm:flex hidden space-x-6'>
        <Link href="/" className='text-white relative after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full'>Home</Link>
         <Link href="/#about" className='text-white relative after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full'>About</Link>
         <Link href="/#speakers" className='text-white relative after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full'>Speakers</Link>
         <Link href="/organisors" className='text-white relative after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full'>organisors</Link>
         <Link href="/timeline" className='text-white relative after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full'>Schedule</Link>
         <Link href="/sponsors" className='text-white relative after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full'>Sponsors</Link>       

        </div>
      {/* mobile */}
      <div className='sm:hidden flex relative'>

      <div className='flex flex-col'>
        <div className='flex justify-center'>
        <button onClick={() => setToggleDropdown(!toggleDropdown)}>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-white">
            <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25H12" />
          </svg>
        </button>
        </div>

      {toggleDropdown && (
              <div className='dropdown font-bold'>
         <Link href="/" className='text-white relative after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full'>Home</Link>
         <Link href="/#about" className='text-white relative after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full'>About</Link>
         <Link href="/#tracks" className='text-white relative after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full'>Tracks</Link>
         <Link href="/timeline" className='text-white relative after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full'>Schedule</Link>
         <Link href="/#speakers" className='text-white relative after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full'>Speakers</Link>
         <Link href="/sponsors" className='text-white relative after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:bg-white after:transition-all after:duration-300 hover:after:w-full'>Sponsors</Link>       

        
                </div>
              )}
      </div>
      </div>

    </nav>
  );
};

export default Navbar