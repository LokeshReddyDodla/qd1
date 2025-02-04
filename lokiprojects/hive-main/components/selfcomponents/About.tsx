import React from 'react';
import { Code2, Blocks, Zap } from 'lucide-react';
import { HyperText } from "@/components/ui/hyper-text";
import { HoverEffect } from "@/components/ui/card-hover-effect";


export const projects = [
  {
    id:1,
    title: 'Build Innovative Solutions',
    description: 'Create groundbreaking applications using cutting-edge technologies and frameworks.',
  },
  {
    id:2,
    title: 'Connect with Experts',
    description: 'Network with industry leaders and get mentorship from experienced developers.',
  },
  {
    id:3,
    title: 'Win Amazing Prizes',
    description: 'Compete for substantial prizes and opportunities to launch your project with industry support.',
  },]


const About = () => {
  return (
    <div id="about" className="py-24 bg-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="font-mono text-4xl font-extrabold text-white sm:text-5xl">
           <HyperText >About the Hackathon </HyperText>
          </h2>
          <p className="mt-4 max-w-2xl mx-auto text-xl text-white/80 font-sans">
          Hack to the Hive is a platform that brings together visionaries, technologists, and entrepreneurs to explore groundbreaking ideas, foster collaboration, and develop transformative solutions.
          </p>
        </div>
        <div className="max-w-5xl mx-auto px-8 flex justify-right">
          <HoverEffect items={projects} />
        </div>

              </div>
    </div>
  );
};

export default About