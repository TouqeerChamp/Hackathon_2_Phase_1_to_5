'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import Link from 'next/link';
import { useAuth } from '@/context/auth-context';
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
  password: z.string().min(1, 'Password is required'),
});

export default function LoginPage() {
  const { login } = useAuth();
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
      const res = await api.post('/api/v1/auth/login', values);
      const token = res.data.access_token || res.data.token;
      if (token) {
          login(token);
      } else {
          setError('Invalid response from server');
      }
    } catch (err: any) {
        if (err.response) {
            setError(err.response.data.detail || 'Login failed');
        } else {
            setError('Login failed');
        }
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#fcfaff] p-4">
      <Card className="w-full max-w-[95%] sm:max-w-md shadow-lg border border-purple-50 bg-white/90 backdrop-blur-sm rounded-2xl">
        <CardHeader className="space-y-2 text-center items-center">
          <div className="rounded-full bg-purple-50 p-3 mb-2">
            <CheckSquare className="h-6 w-6 text-purple-600" />
          </div>
          <CardTitle className="text-3xl font-bold tracking-tight text-slate-900">Welcome back</CardTitle>
          <CardDescription className="text-base text-slate-600">
            Enter your credentials to access your account
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
                Sign In
              </Button>
            </form>
          </Form>
        </CardContent>
        <CardFooter className="justify-center">
          <p className="text-sm text-slate-600 text-center">
            Don't have an account?{' '}
            <Link
              href="/register"
              className="font-semibold text-purple-600 hover:underline underline-offset-4 transition-all"
            >
              Sign up today
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}
