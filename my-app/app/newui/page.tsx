import Image from "next/image";
import { MultisigForm } from "./_components/tokenform";

export default function Home() {
  return (
    <main className="grid min-h-screen grid-cols-4 items-center justify-between p-24">
      <div className="w-full items-center font-mono text-lg lg:flex">
        Tezos Studio.
      </div>
      <div className="z-10 max-w-5xl col-span-3 w-full items-center justify-between font-mono text-sm lg:flex">
        <MultisigForm />
      </div>
    </main>
  );
}
