"use client";
import React from "react";
import { BackgroundGradient } from "@/components/ui/background-gradient";
import Image from "next/image";
import { HyperText } from "@/components/ui/hyper-text";

const cardData = [
  {
    title: "Generative-AI",
    description: "Harness AI to generate dynamic content and craft personalized experiences for diverse digital platforms.",
    image: "/images/tracks/gen-ai.jpg"
  },
  {
    title: "Web3",
    description: "Build decentralized apps that empower users with transparency, security, and full control over digital interactions.",
    image: "/images/tracks/web3.jpg"
  },
  {
    title: "Web2",
    description: "Elevate web experiences by integrating AI-driven solutions into traditional platforms with cutting-edge technology.",
    image: "/images/tracks/web-2.jpg"
  },
  {
    title: "Open Source",
    description: "Contribute to collaborative projects that drive technological progress and shape the future of open innovation.",
    image: "/images/tracks/open-source.jpg"
  }
  
];

export default function Tracks() {
  return (
    <section className="bg-[url('/hero2.jpg')] bg-contain overflow-hidden">
      <div id="about" className="py-12 pb-5 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="font-mono text-4xl font-extrabold text-white sm:text-5xl">
              <HyperText>tracks</HyperText>
            </h2>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 p-6">
        {cardData.map((card, index) => (
          <BackgroundGradient
            key={index}
            className="rounded-[22px] max-w-sm p-4 sm:p-10 bg-zinc-900"
          >
            <div className="relative w-full" style={{ paddingBottom: "100%" }}>
              <Image
                src={card.image}
                alt={card.title}
                layout="fill"
                objectFit="cover"
                className="rounded-lg"
              />
            </div>
            <p className="text-base sm:text-xl mt-4 mb-2 text-neutral-200 font-poppins">
              {card.title}
            </p>
            <p className="text-sm text-neutral-400 font-poppins">
              {card.description}
            </p>
          </BackgroundGradient>
        ))}
      </div>
    </section>
  );
}