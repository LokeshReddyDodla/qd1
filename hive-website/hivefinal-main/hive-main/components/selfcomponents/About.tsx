"use client"
import {useRef,useEffect} from 'react';
import { HyperText } from "@/components/ui/hyper-text";
import { HoverEffect } from "@/components/ui/card-hover-effect";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";



export const projects = [
  {
    id:1,
    title: 'Build Innovative Solutions',
    description: 'Create groundbreaking applications using cutting-edge blockchain technology and Web3 frameworks.',
  },
  {
    id:2,
    title: 'Connect with Experts',
    description: 'Network with industry leaders and get mentorship from experienced blockchain developers.',
  },
  {
    id:3,
    title: 'Win Amazing Prizes',
    description: 'Compete for substantial prizes and opportunities to launch your project with industry support.',
  },]


const About = () => {
  const sectionRef = useRef(null);
  const headingRef = useRef(null);
  const descriptionRef = useRef(null);
  const projectsRef = useRef(null);

  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);
    
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: sectionRef.current,
        start: "top center",
        end: "bottom center",
        toggleActions: "play none none reverse"
      }
    });

    tl.fromTo(headingRef.current,
      { opacity: 0, y: 50 },
      { opacity: 1, y: 0, duration: 0.6 }
    )
    .fromTo(descriptionRef.current,
      { opacity: 0, x: -30 },
      { opacity: 1, x: 0, duration: 0.8 },
      "-=0.3"
    )
    .fromTo(projectsRef.current,
      { opacity: 0, x: -30 },
      { opacity: 1, x: 0, duration: 0.8 },
      "-=0.3"
    );

    return () => {
      ScrollTrigger.getAll().forEach(trigger => trigger.kill());
    };
  }, []);

  return (
    <div id="about" className="pt-24 bg-black bg-[url('/hero2.jpg')] bg-contain overflow-hidden" ref={sectionRef} >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 ">
        <div className="text-center">
          <h2 className="font-mono text-4xl font-extrabold text-white sm:text-5xl" ref={headingRef}>
           <HyperText >why hack to the hive
           </HyperText>
          </h2>
          <p className="mt-4 max-w-4xl mx-auto text-xl text-white/80 font-poppins text-justify " ref={descriptionRef}>
          This event offers a unique platform to collaborate, innovate, and solve real-world challenges in Gen AI, Web 2, Web 3, and open-source technologies. With 30 hours of coding, expert mentorship, and networking, participants gain hands-on experience, sharpen their skills, and create impactful solutions. It’s the perfect opportunity to push boundaries, learn from industry leaders, and make a meaningful impact in the tech community.
          </p>
        </div>

        <div className="max-w-5xl mx-auto px-8 font-poppins"ref={projectsRef}>
      <HoverEffect items={projects} />
    </div>

              </div>
    </div>
  );
};

export default About