"use client";
import { HyperText } from "@/components/ui/hyper-text";
import Image from "next/image";
import React from "react";

// Sample partner data for each tier. Replace the dummy data with your actual partners.
const partnersData = {
  title: [
    {
      name: "Title Partner 1",
      logo: "/images/title-partner1.png",
      link: "https://example.com",
      description:
        "We are looking for partner. Join us now ",
    },
    // Add more title partners as needed
  ],
  venue: [
    {
      name: "Marri Laxman Reddy Institute of Technology and Management",
      logo: "/mlritmsp.jpeg",
      link: "https://www.mlritm.ac.in/",
    },
    // Add more venue partners as needed
  ],
  platinum: [
    {
      name: "Platinum Partner 1",
      logo: "/xyz.png",
      link: "https://example.com",
    },
    {
      name: "Platinum Partner 2",
      logo: "/xyz.png",
      link: "https://example.com",
    },
    // Add more platinum partners as needed
  ],
  gold: [
    {
      name: "Gold Partner 1",
      logo: "/xyz.png",
      link: "https://example.com",
    },
    // Add more gold partners as needed
  ],
  Platform: [
    {
      name: "Gold Partner 1",
      logo: "/H2S.png",
      link: "https://hack2skill.com/",
    },
    // Add more gold partners as needed
  ],
  
  inkind: [
    {
      name: "In-Kind Partner 1",
      logo: "/xyz.png",
      link: "https://gen.xyz/",
    },
    // Add more inkind partners as needed
  ],
  community: [
    {
      name: "NEXUS Swarm",
      logo: "/nexus.jpeg",
      link: "https://linktr.ee/nexus_swarm",
    },
    // Add more inkind partners as needed
  ],
};

export default function PartnersPage() {
  return (
    <div className="w-full py-20 bg-white dark:bg-neutral-900">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl md:text-5xl font-anton font-bold text-center text-neutral-800 dark:text-neutral-200 mb-12">
        <HyperText >PARTNERS </HyperText>
        </h1>
        {Object.entries(partnersData).map(([tier, partners]) => (
          <section key={tier} className="mb-16">
            <h2 className="text-2xl md:text-4xl  font-anton text-center text-neutral-700 dark:text-neutral-300 mb-6 uppercase">
              {tier} Partners
            </h2>
            <div className="flex flex-wrap justify-center gap-8">
              {partners.map(({partner, index}:any) => {
                // Conditional sizing for each tier
                const containerClasses =
                  tier === "title"
                    ? "w-[40rem] h-[20rem]" // Title partner box size
                    : tier === "venue"
                    ? "w-[30rem] h-[20rem]" // Venue partner box size
                    : "w-40 h-40"; // Default size for other tiers

                return (
                  <a
                    key={index}
                    href={partner.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`flex flex-col items-center justify-center p-4 border border-neutral-200 dark:border-neutral-700 rounded-lg hover:shadow-lg transition duration-300 ${containerClasses}`}
                  >
                    {tier === "title" ? (
                      // Title partner box with powered by, partner name, and description
                      <div className="flex w-full h-full">
                        <div className="flex flex-col justify-center w-1/2 p-4">
                          <span className="text-sm text-neutral-600 dark:text-neutral-400">Powered by</span>
                          <h3 className="text-xl md:text-3xl font-bold font-poppins text-neutral-800 dark:text-neutral-200 mt-2">
                            {partner.name}
                          </h3>
                          <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-4">
                            {partner.description ? partner.description:null}
                          </p>
                        </div>
                        <div className="w-1/2 p-4 flex items-center justify-center">
                          <Image
                            src={partner.logo}
                            alt={partner.name}
                            width={200}
                            height={150}
                            className="object-contain"
                          />
                        </div>
                      </div>
                    ) : tier === "venue" ? (
                      // Venue partner box with full image filling the box
                      <div className="w-full h-full relative">
                        <Image
                          src={partner.logo}
                          alt={partner.name}
                          layout="fill" // Ensures the image fills the container
                          className="object-cover rounded-lg"
                        />
                      </div>
                    ) : (
                      // For other tiers, just display logo with name
                      <div className="flex flex-col items-center justify-center">
                        <Image
                          src={partner.logo}
                          alt={partner.name}
                          width={150}
                          height={100}
                          className="object-contain"
                        />
                        <span className="mt-2 text-center text-sm text-neutral-700 dark:text-neutral-300">
                          {partner.name}
                        </span>
                      </div>
                    )}
                  </a>
                );
              })}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
