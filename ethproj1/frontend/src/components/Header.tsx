'use client'

import React from 'react'
import { ConnectButton } from '@rainbow-me/rainbowkit'
import Link from 'next/link'

const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <Link href="/" className="text-2xl font-bold text-primary-600">
              FinancialNFT Barter
            </Link>
            
            <nav className="hidden md:flex space-x-6">
              <Link 
                href="/" 
                className="text-gray-600 hover:text-gray-900 font-medium"
              >
                Portfolio
              </Link>
              <Link 
                href="/marketplace" 
                className="text-gray-600 hover:text-gray-900 font-medium"
              >
                Marketplace
              </Link>
              <Link 
                href="/my-trades" 
                className="text-gray-600 hover:text-gray-900 font-medium"
              >
                My Trades
              </Link>
            </nav>
          </div>
          
          <div className="flex items-center space-x-4">
            <ConnectButton />
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header 