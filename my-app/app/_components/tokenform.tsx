"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useState } from "react";
import { z } from "zod";
import axios from "axios";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "@/components/ui/use-toast";

import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
const items = [
  {
    id: "can_mint",
    label: "Can Mint",
  },
  {
    id: "can_pause",
    label: "Can Pause",
  },
  {
    id: "blacklist",
    label: "Blacklist",
  },
  {
    id: "burn",
    label: "Burn",
  },
] as const;

const formSchema = z.object({
  token_name: z.string().min(1).trim(),
  symbol: z.string().min(1).max(5).trim(),
  initial_supply: z.number().positive(),
  decimals: z.number().int().min(1).max(18),
  initial_owner: z.string().regex(/tz[1-3][1-9A-HJ-NP-Za-km-z]{33}/),
  items: z.array(z.string()).refine((value) => value.some((item) => item), {
    message: "You have to select at least one item.",
  }),
  image_link: z.string(),
});

export function TokenForm() {
  // 1. Define your form.
  const [link, setLink] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      token_name: "",
      symbol: "",
      initial_supply: 1,
      decimals: 1,
      initial_owner: "",
      items: [],
      image_link: "",
    },
  });

  async function submitDataAndRedirect(data: { [key: string]: any }) {
    try {
      // Perform the Axios POST call
      setLink(null);
      setIsLoading(true);
      const response = await axios.post("http://127.0.0.1:8000/create", data);
      console.log(response);
      // Check if the response is successful
      if (response.status == 200) {
        // Redirect the user
        // window.location.href = "/deploy";
        let response_data = response.data;
        setLink(
          "https://smartpy.io/explorer?address=" +
            response.data["contractAddress/errorMessage"]
        );
        // redirect('/deploy');
      } else {
        // Handle unsuccessful response
        console.error("Error: ", response.status);
        // Optionally, provide feedback to the user
      }
    } catch (error: any) {
      // Handle any errors that occur during the call
      console.error("Error during Axios call:", error.message);
      // Optionally, provide feedback to the user
    }
  }

  // 2. Define a submit handler.
  function onSubmit(values: z.infer<typeof formSchema>) {
    // Do something with the form values.
    // ✅ This will be type-safe and validated.

    let data: { [key: string]: any } = {};
    for (const key in values) {
      if (key !== "items") {
        (data as any)[key] = (values as any)[key];
      }
    }

    for (const item of items) {
      console.log(item.id);
      if (values["items"].includes(item.id)) {
        data[item.id] = true;
      } else {
        data[item.id] = false;
      }
    }
    console.log(data);
    toast({
      title: "You submitted the following values:",
      description: (
        <pre className="mt-2 w-[340px] rounded-md bg-slate-950 p-4">
          <code className="text-white">{JSON.stringify(data, null, 2)}</code>
        </pre>
      ),
    });

    submitDataAndRedirect(data);
  }

  return (
    <div>
      {isLoading && !link && <h1>Loading...</h1>}
      {isLoading || (
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="grid grid-cols-2 gap-4"
          >
            <FormField
              control={form.control}
              name="token_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Token Name</FormLabel>
                  <FormControl>
                    <Input placeholder="token" {...field} />
                  </FormControl>
                  <FormDescription></FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="symbol"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Symbol</FormLabel>
                  <FormControl>
                    <Input placeholder="symbol" {...field} />
                  </FormControl>
                  <FormDescription></FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="decimals"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Decimals</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="shadcn"
                      {...field}
                      onChange={(event) => field.onChange(+event.target.value)}
                    />
                  </FormControl>
                  <FormDescription></FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="initial_supply"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Intial Supply</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="supply"
                      {...field}
                      onChange={(event) => field.onChange(+event.target.value)}
                    />
                  </FormControl>
                  <FormDescription></FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="initial_owner"
              render={({ field }) => (
                <FormItem className="col-span-2">
                  <FormLabel>Initial Owner</FormLabel>
                  <FormControl>
                    <Input placeholder="owner" {...field} />
                  </FormControl>
                  <FormDescription>This is your address.</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="items"
              render={() => (
                <FormItem>
                  <div className="mb-4">
                    <FormLabel className="text-base">
                      Additional Contract Functions
                    </FormLabel>
                    <FormDescription>
                      Select the items you want to add to the contract.
                    </FormDescription>
                  </div>
                  {items.map((item) => (
                    <FormField
                      key={item.id}
                      control={form.control}
                      name="items"
                      render={({ field }) => {
                        return (
                          <FormItem
                            key={item.id}
                            className="flex flex-row items-start space-x-3 space-y-0"
                          >
                            <FormControl>
                              <Checkbox
                                checked={field.value?.includes(item.id)}
                                onCheckedChange={(checked) => {
                                  return checked
                                    ? field.onChange([...field.value, item.id])
                                    : field.onChange(
                                        field.value?.filter(
                                          (value) => value !== item.id
                                        )
                                      );
                                }}
                              />
                            </FormControl>
                            <FormLabel className="text-sm font-normal">
                              {item.label}
                            </FormLabel>
                          </FormItem>
                        );
                      }}
                    />
                  ))}
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="image_link"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Image Link</FormLabel>
                  <FormControl>
                    <Input placeholder="image" {...field} />
                  </FormControl>
                  <FormDescription></FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" className="justify-self-center col-span-2">
              Submit
            </Button>
          </form>
        </Form>
      )}
      {link && (
        <a target="_blank" className="text-lg underline" href={link}>
          Visit Link
        </a>
      )}
    </div>
  );
}
