'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { CheckSquare } from 'lucide-react';

const formSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

export default function RegisterPage() {
  const router = useRouter();
  const [error, setError] = useState('');

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
  try {
    setError('');
    // Backend 'username' mangta hai
    await api.post('/auth/register', {
      username: values.email, 
      password: values.password,
    });
    router.push('/login');
  } catch (err: any) {
    // Crash se bachne ke liye safe error handling
    const detail = err.response?.data?.detail;
    const message = Array.isArray(detail) ? detail[0].msg : (typeof detail === 'string' ? detail : "Registration failed");
    setError(message);
  }
}

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#fcfaff] p-4">
      <Card className="w-full max-w-[95%] sm:max-w-md shadow-lg border border-purple-50 bg-white/90 backdrop-blur-sm rounded-2xl">
        <CardHeader className="space-y-2 text-center items-center">
          <div className="rounded-full bg-purple-50 p-3 mb-2">
            <CheckSquare className="h-6 w-6 text-purple-600" />
          </div>
          <CardTitle className="text-3xl font-bold tracking-tight text-slate-900">Create an account</CardTitle>
          <CardDescription className="text-base text-slate-600">
            Enter your email below to create your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="font-medium text-slate-900">Email</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="email@example.com"
                        className="h-11 bg-white focus:border-purple-400 focus:ring-purple-100 transition-colors"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="font-medium text-slate-900">Password</FormLabel>
                    <FormControl>
                      <Input
                        type="password"
                        className="h-11 bg-white focus:border-purple-400 focus:ring-purple-100 transition-colors"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              {error && (
                <div className="p-3 rounded-lg bg-red-50 text-red-600 text-sm font-medium text-center">
                  {error}
                </div>
              )}
              <Button type="submit" className="w-full h-11 text-base shadow-md hover:shadow-lg transition-all bg-purple-600 hover:bg-purple-700 text-white">
                Create Account
              </Button>
            </form>
          </Form>
        </CardContent>
        <CardFooter className="justify-center">
          <p className="text-sm text-slate-600 text-center">
            Already have an account?{' '}
            <a
  href="/login"
  className="font-semibold text-purple-600 hover:underline underline-offset-4 transition-all"
>
  Sign in
</a>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}
