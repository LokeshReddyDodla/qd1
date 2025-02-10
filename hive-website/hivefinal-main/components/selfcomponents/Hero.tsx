"use client";
import React from "react";
import { TextAnimate } from "@/components/ui/text-animate";
import { InteractiveHoverButton } from "@/components/ui/interactive-hover-button";
import { ShootingStars } from "@/components/ui/shooting-stars";
import { StarsBackground } from "@/components/ui/stars-background";

const Hero = () => {
  const handleClick = () => {
    window.location.href = "https://vision.hack2skill.com/event/hacktothehive"; // Replace with your desired URL
  };

  return (
    <div className="relative min-h-screen bg-black overflow-hidden">
      <StarsBackground />
      <ShootingStars />
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-[20%] flex items-center justify-between">
        <div className="max-w-3xl text-left">
          <h1 className="font-mono text-[9rem] leading-none text-white tracking-tighter animate-title">
            <TextAnimate animation="fadeIn" by="line" as="div" className="font-anton">
              {`HACK TO\n\nTHE HIVE`}
            </TextAnimate>
          </h1>
          <div className="mt-12 flex flex-wrap gap-4">
            <InteractiveHoverButton onClick={handleClick}>Launch Now</InteractiveHoverButton>
          </div>
        </div>
        <div className="max-w-lg lg:max-w-xl xl:max-w-2xl">
          <img src="/space.png" alt="3DSpaceTheme" className="w-full h-auto" />
        </div>
      </div>
    </div>
  );
};

export default Hero;
