"use client"
import React, { useEffect, useRef } from 'react';
import { TextAnimate } from "@/components/ui/text-animate";

const Hero = () => {
  const starsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const generateStars = () => {
      if (!starsRef.current) return;
      const stars = starsRef.current;
      stars.innerHTML = '';
      
      for (let i = 0; i < 100; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;
        star.style.animationDelay = `${Math.random() * 3}s`;
        stars.appendChild(star);
      }
    };

    generateStars();
  }, []);

  return (
    <div className="relative min-h-screen bg-[url('/hero2.jpg')] bg-cover bg-right overflow-hidden">
      <div ref={starsRef} className="absolute inset-0 z-0" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-[15%]">
        <div className="max-w-3xl">
        
          <h1 className="font-anton text-[9rem] leading-none text-white tracking-tighter animate-title font-bold
            sm:text-[6rem] md:text-[7rem] lg:text-[9rem]"> {/* Added responsive text sizes */}
            <TextAnimate animation="fadeIn" by="line" as="div">
              {`HACK TO\n\nTHE HIVE`}
            </TextAnimate>
          </h1>

          <div className="mt-16 flex flex-wrap gap-4">
            <a
              href="#register"
              className="font-mono group relative inline-flex items-center px-8 py-3 bg-transparent border border-white text-white text-lg font-bold rounded-lg overflow-hidden transition-all duration-300"
            >
              <span className="relative z-10">REGISTER NOW</span>
              <div className="absolute inset-0 bg-white/10 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></div>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Hero;
