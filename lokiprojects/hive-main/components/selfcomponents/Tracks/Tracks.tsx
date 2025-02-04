"use client";
import React from "react";
import { BackgroundGradient } from "@/components/ui/background-gradient";
import Image from "next/image";
import { HyperText } from "@/components/ui/hyper-text";

const cardData = [
  {
    title: "Generative-AI",
    description: "Leverage AI to create dynamic content and personalized experiences across various platforms.",
    image: "/hero.jpg",
  },
  {
    title: "Web3 Techonology",
    description: "Develop decentralized applications that empower users with control and transparency in decentralized internet",
    image: "/hero.jpg",
  },
  {
    title: "Web2 Techonology",
    description: "Enhance user experiences by integrating advanced AI capabilities into traditional web platforms",
    image: "/hero.jpg",
  },
  {
    title: "Open Source",
    description: "Contribute to and benefit from community-driven projects that accelerate technological advancement.",
    image: "/hero.jpg",
  },
];

export default function Tracks() {
  return (
    <>
      <div id="about" className="py-24 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="font-mono text-4xl font-extrabold text-white sm:text-5xl">
              <HyperText>tracks</HyperText>
            </h2>
            <p className="mt-4 max-w-2xl mx-auto text-xl text-white/80 font-sans">
              Join us in pushing the boundaries of blockchain technology and Web3 innovation
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 p-6">
        {cardData.map((card, index) => (
          <BackgroundGradient
            key={index}
            className="rounded-[22px] max-w-sm p-4 sm:p-10 bg-zinc-900"
          >
            <Image
              src={card.image}
              alt={card.title}
              height="400"
              width="400"
              className="object-cover rounded-lg"
            />
            <p className="text-base sm:text-xl mt-4 mb-2 text-neutral-200">
              {card.title}
            </p>
            <p className="text-sm text-neutral-400">
              {card.description}
            </p>
            <button className="rounded-full px-4 py-2 text-white mt-4 text-xs font-bold bg-zinc-800">
              Learn More
            </button>
          </BackgroundGradient>
        ))}
      </div>
    </>
  );
}
