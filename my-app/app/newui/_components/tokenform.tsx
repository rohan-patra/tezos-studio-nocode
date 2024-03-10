"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";

const partnerSchema = z.object({
  address: z.string().regex(/tz[1-3][1-9A-HJ-NP-Za-km-z]{33}/),
  power: z.number().min(0).max(100),
});

const formSchema = z.object({
  contract_name: z.string().min(1),
  partners: z.array(partnerSchema),
  quorum: z.number().min(0).max(100),
});

export function MultisigForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      contract_name: "",
      partners: [{ address: "", power: 1 }],
      quorum: 50,
    },
  });

  const { fields, append, remove } = useFieldArray({
    name: "partners",
    control: form.control,
  });

  function onSubmit(data: z.infer<typeof formSchema>) {
    console.log(data);
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="w-2/3 space-y-6">
        <FormField
          control={form.control}
          name="contract_name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Multisig wallet contract name*</FormLabel>
              <FormControl>
                <Input placeholder="Contract name" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        {fields.map((field, index) => (
          <div key={field.id} className="flex space-x-4">
            <FormField
              control={form.control}
              name={`partners.${index}.address`}
              render={({ field }) => (
                <FormItem className="flex-1">
                  <FormLabel>Partner Address*</FormLabel>
                  <FormControl>
                    <Input placeholder="Partner Address" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name={`partners.${index}.power`}
              render={({ field }) => (
                <FormItem className="flex-1">
                  <FormLabel>Power*</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      placeholder="Power"
                      min={0}
                      max={100}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button
              type="button"
              variant="destructive"
              onClick={() => remove(index)}
              className="h-10 self-end"
            >
              Remove
            </Button>
          </div>
        ))}
        <Button type="button" onClick={() => append({ address: "", power: 1 })}>
          Add Partner
        </Button>
        <FormField
          control={form.control}
          name="quorum"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Quorum %</FormLabel>
              <FormControl>
                <Slider
                  value={[field.value]}
                  onValueChange={(value) => field.onChange(value[0])}
                  max={100}
                  step={1}
                />
              </FormControl>
              <div className="mt-2 text-sm text-gray-500">
                Current Quorum: {field.value}%
              </div>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  );
}
