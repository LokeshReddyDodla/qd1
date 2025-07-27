'use client'

import React from 'react'
import { ConnectButton } from '@rainbow-me/rainbowkit'
import { useAccount } from 'wagmi'
import Header from '@/components/Header'
import PortfolioDashboard from '@/components/PortfolioDashboard'
import WelcomeScreen from '@/components/WelcomeScreen'

export default function Home() {
  const { address, isConnected } = useAccount()

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {isConnected ? (
          <PortfolioDashboard address={address} />
        ) : (
          <WelcomeScreen />
        )}
      </main>
    </div>
  )
} 