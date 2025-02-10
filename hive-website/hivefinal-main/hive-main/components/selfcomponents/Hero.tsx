"use client"
import React, { useEffect, useRef } from 'react';
import { TextAnimate } from "@/components/ui/text-animate";
import { InteractiveHoverButton } from "@/components/ui/interactive-hover-button";  

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
    <div className="relative min-h-screen bg-[url('/hero.jpg')] bg-cover bg-right
 overflow-hidden">
      <div ref={starsRef} className="absolute inset-0 z-0" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-[5%]">
        <div className="max-w-3xl">
        
          <h1 className="font-mono text-[9rem] leading-none text-white tracking-tighter animate-title">
          <TextAnimate animation="fadeIn" by="line" as="div" className=' font-anton'>
      {`HACK TO\n\nTHE HIVE`}
           </TextAnimate>
          </h1>

          <div className="mt-12 flex flex-wrap gap-4">
            <InteractiveHoverButton>REGISTER</InteractiveHoverButton>;
          </div>
        </div>
      </div>

      </div>
  );
};

export default Hero