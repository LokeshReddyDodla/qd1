"use client"
import {useEffect, useRef} from 'react'
import { HyperText } from '../ui/hyper-text'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
gsap.registerPlugin(ScrollTrigger)


function Aboutus() {

    const headingRef = useRef(null)
    const textRef1 = useRef(null)
    
    
  useEffect(() => {
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: "#about",
        start: "top 80%",
        toggleActions: "play none none reverse"
      }
    });

    tl.fromTo(headingRef.current,
      { 
        opacity: 0, 
        x: -50
      },
      {
        opacity: 1,
        x: 0,
        duration: 1,
      }
    )
    .fromTo(textRef1.current,
      { 
        opacity: 0, 
        x: -30,
      },
      {
        opacity: 1,
        x: 0,
        duration: 1,
        stagger: {
          amount: 0.5,
          from: "start",
          ease: "power2.out"
        }
      },
       // Start slightly before the previous animation ends
    );

  }, []);

    

  return (
    
        <section id="about" className="pt-24 bg-[url('/hero2.jpg')] bg-contain overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 ref={headingRef} className=" font-anton text-4xl font-extrabold text-white sm:text-5xl">
           <HyperText >About us </HyperText>
          </h2>
          <p ref={textRef1} className="mt-4 max-w-4xl mx-auto text-xl text-white/80 font-poppins text-justify">
          Hack to the Hive is an international hackathon that brings together passionate innovators to solve exciting technological challenges. It provides a collaborative space where participants can transform their ideas into impactful solutions while gaining valuable insights from expert mentors.
          <br /><br />
          Over the course of 30 hours, participants will experience hands-on coding, creative problem-solving, and opportunities to learn and grow in a competitive yet supportive environment. Join us to push the boundaries of technology, connect with like-minded individuals, and leave a lasting impact on the tech community.
        </p>     
         </div>
        </div>
        </section>
      
    
  )
}

export default Aboutus
