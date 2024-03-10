"use client"

import React from 'react'
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {Button} from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"

export default function page() {

  function changePage() {
    window.location.href = "/newui";
  }

  return (
    <main className="grid grid-cols-2 gap-4 place-content-center min-h-screen items-center justify-between p-24">
      <div className="font-mono text-lg justify-self-center">
        Import Contract
        </div>
    <div className="grid w-full max-w-sm items-center font-mono">
      <Label htmlFor="picture"> Smart Contract Specifications</Label>
      <Separator className="my-4" />
      <Input id="picture" type="file"/>
      <Button className = "my-4 w-32 justify-self-center" onClick = {() => changePage()}> Submit</Button>
    </div>
    </main>
  )
}
