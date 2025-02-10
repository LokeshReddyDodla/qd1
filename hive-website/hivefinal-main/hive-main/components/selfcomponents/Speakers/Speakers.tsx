"use client";

import Image from "next/image";
import React from "react";
import { CardBody, CardContainer, CardItem } from "@/components/ui/3d-card";
import Link from "next/link";
import { FaLinkedinIn } from "react-icons/fa";
import { FaXTwitter } from "react-icons/fa6";
import { HyperText } from "@/components/ui/hyper-text";
import { ShinyButton } from "@/components/ui/shiny-button";

const cardData = [
  {
    name: "Dr. Sarah Chen",
    role: "Blockchain Researcher",
    company: "Web3 Institute",
    image: "/hero.jpg",
    linkedin: "https://linkedin.com",
    twitter: "https://twitter.com",
  },
  {
    name: "Michael Rodriguez",
    role: "Chief Innovation Officer",
    company: "DeFi Solutions",
    image: "/hero.jpg",
    linkedin: "https://linkedin.com",
  },
  {
    name: "Emily Carter",
    role: "Web3 Developer",
    company: "MetaChain Labs",
    image: "/hero.jpg",
    linkedin: "https://linkedin.com",
    twitter: "https://twitter.com",
  },
  {
    name: "John Doe",
    role: "Crypto Analyst",
    company: "Blockchain Insights",
    image: "/hero.jpg",
    linkedin: "https://linkedin.com",
  },
];

export default function Speakers() {
  return (
    <>
      <div id="about" className="py-24 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="font-mono text-4xl font-extrabold text-white sm:text-5xl">
            <HyperText>Speakers</HyperText>
          </h2>
          <p className="mt-4 max-w-2xl mx-auto text-xl text-white/80 font-sans">
            Join us in pushing the boundaries of blockchain technology and Web3 innovation
          </p>
        </div>
      </div>

      {/* Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 p-6 max-w-7xl mx-auto">
        {cardData.map((person, index) => (
          <CardContainer key={index} className="inter-var">
            <CardBody className="relative group/card dark:hover:shadow-2xl dark:hover:shadow-emerald-500/[0.1] bg-black border-white/[0.2] w-full max-w-[20rem] h-auto rounded-xl p-6 border transition-all duration-300">
              <CardItem translateZ="50" className="w-full flex justify-center">
                <Image
                  src={person.image}
                  height={500}
                  width={400}
                  className="object-cover border border-gray-300 rounded-xl"
                  alt={person.name}
                />
              </CardItem>
              <CardItem translateZ="50" className="text-xl font-semibold text-white text-center mt-4">
                {person.name}
              </CardItem>
              <CardItem as="p" translateZ="60" className="text-sm text-center text-neutral-300">
                {person.role} at {person.company}
              </CardItem>
              <div className="flex justify-center gap-4 mt-6">
                <CardItem
                  translateZ={20}
                  as={Link}
                  href={person.linkedin}
                  target="_blank"
                  className="px-4 py-2 rounded-xl text-xs font-normal text-white"
                >
                  <FaLinkedinIn className="h-5 w-5" />
                </CardItem>
                {person.twitter && (
                  <CardItem
                    translateZ={20}
                    as={Link}
                    href={person.twitter}
                    target="_blank"
                    className="px-4 py-2 rounded-xl text-xs font-normal text-white"
                  >
                    <FaXTwitter className="h-5 w-5" />
                  </CardItem>
                )}
              </div>
            </CardBody>
          </CardContainer>
        ))}
      </div>
      {/* join us button */}
      <div className="flex justify-center">
      <ShinyButton>Join us</ShinyButton>      
      </div>      
    </>
  );
}