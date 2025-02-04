import React from 'react';
import { Github, Twitter, Linkedin } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-black py-16 ">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          <div>
            <h3 className="font-mono text-2xl font-bold text-white mb-4">HACK TO THE HIVE</h3>
            <p className="text-white/60 font-sans">
              Join us in building the future of Web3 technology and decentralized innovation.
            </p>
          </div>
          <div>
            <h4 className="font-mono text-lg font-bold text-white mb-4">Quick Links</h4>
            <ul className="space-y-2 font-poppins">
              <li><a href="#about" className="text-white/60 hover:text-white">About</a></li>
              <li><a href="#tracks" className="text-white/60 hover:text-white">Tracks</a></li>
              <li><a href="#schedule" className="text-white/60 hover:text-white">Schedule</a></li>
              <li><a href="#sponsors" className="text-white/60 hover:text-white">Sponsors</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-mono text-lg font-bold text-white mb-4">Connect With Us</h4>
            <div className="flex space-x-4">
              <a href="#" className="text-white/60 hover:text-white">
                <Github className="w-6 h-6" />
              </a>
              <a href="#" className="text-white/60 hover:text-white">
                <Twitter className="w-6 h-6" />
              </a>
              <a href="#" className="text-white/60 hover:text-white">
                <Linkedin className="w-6 h-6" />
              </a>
            </div>
          </div>
        </div>
        <div className="mt-12 pt-8  text-center">
          <p className="text-white/60 font-poppins">© 2024 Hack to the Hive. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;