
import Hero from '@/components/selfcomponents/Hero';
import About from '@/components/selfcomponents/About';
import Prizes from '@/components/selfcomponents/Prizes/Prizes';
import Speakers from '@/components/selfcomponents/Speakers/Speakers';
import Tracks from '@/components/selfcomponents/Tracks/Tracks';
import FAQ from '@/components/selfcomponents/FAQ/FAQ';

import { PastEvents } from '@/components/selfcomponents/pastevents/pastevent';



export default function Home() {
  return (
    <div className="min-h-screen ">
    <main className=' bg-black'>
    
      <Hero />
      <About />
      <PastEvents/>
      <Speakers />
      <Tracks />    
      <Prizes />
      <FAQ />
      
    </main>
  </div>

  );
}
