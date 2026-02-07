'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/protected-route';
import Header from '@/components/header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useAuth } from '@/context/auth-context';
import { CheckSquare, Plus, Search, Trash2, Loader2, RefreshCw, Sparkles, Edit2, X, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { taskService } from '@/lib/api';
import { Task } from '@/types';

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(true);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [isAddingTask, setIsAddingTask] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Edit Mode state
  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [editedTaskTitle, setEditedTaskTitle] = useState('');

  // Agent state
  const [showAgent, setShowAgent] = useState(false);
  const [agentPrompt, setAgentPrompt] = useState('');
  const [isAgentProcessing, setIsAgentProcessing] = useState(false);

  // Strategist Agent state
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<{
    summary: string;
    insights: string[];
    recommendations: string[];
    patterns: string[];
    stats: {
      total: number;
      completed: number;
      pending: number;
      completion_rate: number;
    };
  } | null>(null);

  // Feedback state
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    if (user?.id) {
      loadTasks();
    }
  }, [user?.id]);

  // Auto-dismiss toast
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ message, type });
  };

  const loadTasks = async () => {
    if (!user?.id) return;
    try {
      setIsLoadingTasks(true);
      const data = await taskService.fetchTasks();
      setTasks(data.tasks);
    } catch (error) {
      console.error('Failed to load tasks', error);
      showToast('Failed to load tasks', 'error');
    } finally {
      setIsLoadingTasks(false);
    }
  };

  const handleAddTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim() || !user?.id) return;

    try {
      setIsAddingTask(true);
      const newTask = await taskService.addTask(newTaskTitle);
      setTasks([newTask, ...tasks]);
      setNewTaskTitle('');
      showToast('Task created successfully', 'success');
    } catch (error) {
      console.error('Failed to create task', error);
      showToast('Failed to create task', 'error');
    } finally {
      setIsAddingTask(false);
    }
  };

  const handleToggleTask = async (taskId: number, currentCompleted: boolean) => {
    if (!user?.id) return;

    // Optimistic update
    const previousTasks = [...tasks];
    setTasks(tasks.map(t =>
      t.id === taskId ? { ...t, completed: !currentCompleted, updated_at: new Date().toISOString() } : t
    ));

    try {
      await taskService.toggleTaskStatus(taskId);
    } catch (error) {
      // Revert on failure
      setTasks(previousTasks);
      console.error('Failed to update task', error);
      showToast('Failed to update task status', 'error');
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    if (!user?.id) return;

    // Optimistic update
    const previousTasks = [...tasks];
    setTasks(tasks.filter(t => t.id !== taskId));

    try {
      await taskService.deleteTask(taskId);
      showToast('Task deleted', 'success');
    } catch (error) {
      // Revert on failure
      setTasks(previousTasks);
      console.error('Failed to delete task', error);
      showToast('Failed to delete task', 'error');
    }
  };

  const startEditing = (task: Task) => {
    setEditingTaskId(task.id);
    setEditedTaskTitle(task.title);
  };

  const cancelEditing = () => {
    setEditingTaskId(null);
    setEditedTaskTitle('');
  };

  const saveEditing = async () => {
    if (!editingTaskId || !user?.id || !editedTaskTitle.trim()) return;

    const previousTasks = [...tasks];
    setTasks(tasks.map(t => t.id === editingTaskId ? { ...t, title: editedTaskTitle } : t));
    const taskIdToUpdate = editingTaskId; // Capture ID
    setEditingTaskId(null);

    try {
      await taskService.updateTask(taskIdToUpdate, { title: editedTaskTitle });
      showToast('Task updated', 'success');
    } catch (error) {
      setTasks(previousTasks);
      console.error('Failed to update task', error);
      showToast('Failed to update task', 'error');
    }
  };

  const handleAgentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!agentPrompt.trim()) return;

    setIsAgentProcessing(true);

    try {
      const result = await taskService.agentPrompt(agentPrompt);
      showToast(result.response, 'success');
      setAgentPrompt('');
      await loadTasks();
    } catch (error) {
      console.error('Agent error:', error);
      showToast('Agent failed to process command', 'error');
    } finally {
      setIsAgentProcessing(false);
    }
  };

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    setShowAnalysis(true);

    try {
      const result = await taskService.analyzeTask();
      setAnalysis(result);
      showToast('Analysis complete!', 'success');
    } catch (error) {
      console.error('Analysis error:', error);
      showToast('Failed to analyze tasks', 'error');
      setShowAnalysis(false);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Filtered tasks
  const filteredTasks = tasks.filter(task =>
    task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    task.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <ProtectedRoute>
      <div className="min-h-screen flex flex-col transition-colors duration-300 relative bg-[#fcfaff]">
        <Header />

        {/* Toast Notification */}
        {toast && (
          <div className={`fixed top-20 right-4 z-50 px-4 py-2 rounded-lg shadow-lg text-white animate-in slide-in-from-right-5 fade-in duration-300 ${
            toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'
          }`}>
            <div className="flex items-center gap-2">
              {toast.type === 'success' ? <CheckSquare className="h-4 w-4" /> : <RefreshCw className="h-4 w-4" />}
              <span className="font-medium">{toast.message}</span>
            </div>
          </div>
        )}

        <main className="flex-1 container mx-auto px-4 py-8 sm:px-6 lg:px-8 max-w-full md:max-w-5xl">
          {/* Welcome Section */}
          <div className="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">
                Dashboard
              </h1>
              <p className="text-lg text-slate-600 mt-2">
                Manage your tasks efficiently, {user?.email?.split('@')[0]}.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
               <Button
                 variant="outline"
                 size="lg"
                 className="shadow-md hover:shadow-lg transition-all gap-2 border-purple-200 bg-purple-50 text-purple-700 hover:bg-purple-100"
                 onClick={() => setShowAgent(!showAgent)}
               >
                 <Sparkles className="h-5 w-5" /> Magic Assistant
               </Button>
               <Button
                 variant="outline"
                 size="lg"
                 className="shadow-md hover:shadow-lg transition-all gap-2 border-purple-200 bg-purple-50 text-purple-700 hover:bg-purple-100"
                 onClick={handleAnalyze}
                 disabled={isAnalyzing}
               >
                 {isAnalyzing ? (
                   <Loader2 className="h-5 w-5 animate-spin" />
                 ) : (
                   <Sparkles className="h-5 w-5" />
                 )}
                 AI Suggestions
               </Button>
            </div>
          </div>

          {/* Agent Section */}
          {showAgent && (
              <Card className="mb-8 border-purple-50 bg-white/90 shadow-lg backdrop-blur-sm rounded-2xl">
                  <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-purple-700">
                          <Sparkles className="h-5 w-5" /> AI Task Assistant
                      </CardTitle>
                      <CardDescription className="text-slate-600">
                          Describe what you want to do (e.g., "Add a task to buy milk", "Clean up completed tasks")
                      </CardDescription>
                  </CardHeader>
                  <CardContent>
                      <form onSubmit={handleAgentSubmit} className="flex flex-col sm:flex-row gap-4">
                          <Input
                              placeholder="Type your command..."
                              value={agentPrompt}
                              onChange={(e) => setAgentPrompt(e.target.value)}
                              className="flex-1 bg-white focus:border-purple-400 focus:ring-purple-100"
                              disabled={isAgentProcessing}
                          />
                          <Button type="submit" disabled={isAgentProcessing} className="min-w-[100px] bg-purple-600 hover:bg-purple-700 text-white shadow-md">
                              {isAgentProcessing ? <Loader2 className="h-4 w-4 animate-spin" /> : "Execute"}
                          </Button>
                      </form>
                  </CardContent>
              </Card>
          )}

          {/* AI Suggestions / Analysis Section */}
          {showAnalysis && analysis && (
              <Card className="mb-8 border-purple-50 bg-white/90 shadow-lg backdrop-blur-sm rounded-2xl">
                  <CardHeader>
                      <div className="flex items-center justify-between">
                          <CardTitle className="flex items-center gap-2 text-purple-700">
                              <Sparkles className="h-5 w-5" /> AI Task Analysis
                          </CardTitle>
                          <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setShowAnalysis(false)}
                          >
                              <X className="h-4 w-4" />
                          </Button>
                      </div>
                      <CardDescription className="text-base font-medium mt-2 text-slate-600">
                          {analysis.summary}
                      </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                      {/* Statistics */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="bg-purple-50/50 p-4 rounded-lg border border-purple-100">
                              <p className="text-sm text-slate-600">Total Tasks</p>
                              <p className="text-2xl font-bold text-slate-900">{analysis.stats.total}</p>
                          </div>
                          <div className="bg-purple-50/50 p-4 rounded-lg border border-purple-100">
                              <p className="text-sm text-slate-600">Completed</p>
                              <p className="text-2xl font-bold text-green-600">{analysis.stats.completed}</p>
                          </div>
                          <div className="bg-purple-50/50 p-4 rounded-lg border border-purple-100">
                              <p className="text-sm text-slate-600">Pending</p>
                              <p className="text-2xl font-bold text-amber-600">{analysis.stats.pending}</p>
                          </div>
                          <div className="bg-purple-50/50 p-4 rounded-lg border border-purple-100">
                              <p className="text-sm text-slate-600">Completion Rate</p>
                              <p className="text-2xl font-bold text-purple-600">{analysis.stats.completion_rate}%</p>
                          </div>
                      </div>

                      {/* Insights */}
                      {analysis.insights.length > 0 && (
                          <div className="bg-purple-50/50 p-4 rounded-lg border border-purple-100">
                              <h4 className="font-semibold mb-3 flex items-center gap-2 text-slate-900">
                                  💡 Insights
                              </h4>
                              <ul className="space-y-2">
                                  {analysis.insights.map((insight, idx) => (
                                      <li key={idx} className="text-sm text-slate-600 flex items-start gap-2">
                                          <span className="text-purple-600 mt-0.5">•</span>
                                          <span>{insight}</span>
                                      </li>
                                  ))}
                              </ul>
                          </div>
                      )}

                      {/* Recommendations */}
                      {analysis.recommendations.length > 0 && (
                          <div className="bg-purple-50/50 p-4 rounded-lg border border-purple-100">
                              <h4 className="font-semibold mb-3 flex items-center gap-2 text-slate-900">
                                  🎯 Recommendations
                              </h4>
                              <ol className="space-y-2">
                                  {analysis.recommendations.map((rec, idx) => (
                                      <li key={idx} className="text-sm text-slate-600 flex items-start gap-2">
                                          <span className="text-purple-600 font-semibold">{idx + 1}.</span>
                                          <span>{rec}</span>
                                      </li>
                                  ))}
                              </ol>
                          </div>
                      )}

                      {/* Patterns */}
                      {analysis.patterns.length > 0 && (
                          <div className="bg-purple-50/50 p-4 rounded-lg border border-purple-100">
                              <h4 className="font-semibold mb-3 flex items-center gap-2 text-slate-900">
                                  🔍 Patterns Detected
                              </h4>
                              <ul className="space-y-2">
                                  {analysis.patterns.map((pattern, idx) => (
                                      <li key={idx} className="text-sm text-slate-600 flex items-start gap-2">
                                          <span className="text-purple-600 mt-0.5">•</span>
                                          <span>{pattern}</span>
                                      </li>
                                  ))}
                              </ul>
                          </div>
                      )}
                  </CardContent>
              </Card>
          )}

          {/* New Task Input */}
          <Card className="mb-8 border-purple-50 bg-white/90 shadow-lg backdrop-blur-sm rounded-2xl">
            <CardContent className="pt-6">
              <form onSubmit={handleAddTask} className="flex flex-col sm:flex-row gap-4">
                <Input
                  placeholder="What needs to be done?"
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  className="flex-1 h-12 text-lg bg-white focus:border-purple-400 focus:ring-purple-100 transition-colors"
                  disabled={isAddingTask}
                />
                <Button
                  type="submit"
                  size="lg"
                  className="h-12 px-6 shadow-md hover:shadow-lg transition-all bg-purple-600 hover:bg-purple-700 text-white"
                  disabled={isAddingTask || !newTaskTitle.trim()}
                >
                  {isAddingTask ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <>
                      <Plus className="mr-2 h-5 w-5" /> Add Task
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Search & Filter Bar */}
          <div className="mb-8 flex flex-col sm:flex-row items-stretch sm:items-center gap-4 bg-white/90 p-4 rounded-xl border border-purple-50 shadow-lg backdrop-blur-sm">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search tasks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-white focus:border-purple-400 focus:ring-purple-100 shadow-none focus-visible:ring-1"
              />
            </div>
            <div className="hidden sm:flex gap-2">
               <Button variant="ghost" size="sm" className="font-medium text-slate-900">All</Button>
               <Button variant="ghost" size="sm" className="text-slate-600 hover:text-slate-900">Active</Button>
               <Button variant="ghost" size="sm" className="text-slate-600 hover:text-slate-900">Completed</Button>
            </div>
          </div>

          {/* Task List / Empty State */}
          <div className="space-y-4">
            {authLoading || isLoadingTasks ? (
               <div className="grid gap-4">
                 <Skeleton className="h-24 w-full rounded-xl" />
                 <Skeleton className="h-24 w-full rounded-xl" />
                 <Skeleton className="h-24 w-full rounded-xl" />
               </div>
            ) : filteredTasks.length > 0 ? (
               <div className="grid gap-4">
                   {filteredTasks.map((task) => (
                     <Card
                        key={task.id}
                        className={`transition-all hover:shadow-lg border-l-4 shadow-md bg-white/90 backdrop-blur-sm border border-purple-50 rounded-2xl ${
                          task.completed
                            ? 'border-l-green-500 opacity-75'
                            : 'border-l-purple-500 hover:border-purple-600'
                        }`}
                     >
                       <CardContent className="p-4 sm:p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4">
                          <div className="flex items-center gap-3 flex-1 min-w-0">
                            {/* Checkbox */}
                            <button
                              onClick={() => handleToggleTask(task.id, task.completed)}
                              className={`flex-shrink-0 rounded-md p-1 transition-colors ${
                                task.completed ? 'text-green-600 bg-green-50 hover:bg-green-100' : 'text-slate-400 hover:bg-purple-50'
                              }`}
                            >
                              <CheckSquare className={`h-6 w-6 ${task.completed ? 'fill-current' : ''}`} />
                            </button>

                            {/* Task Content / Edit Mode */}
                            <div className="flex-1 min-w-0">
                                {editingTaskId === task.id ? (
                                    <div className="flex items-center gap-2">
                                        <Input
                                            value={editedTaskTitle}
                                            onChange={(e) => setEditedTaskTitle(e.target.value)}
                                            className="h-8 bg-white focus:border-purple-400 focus:ring-purple-100"
                                            autoFocus
                                            onKeyDown={(e) => e.key === 'Enter' && saveEditing()}
                                        />
                                        <Button size="icon" variant="ghost" className="h-8 w-8 text-green-600 hover:text-green-700 hover:bg-green-50" onClick={saveEditing}>
                                            <Check className="h-4 w-4" />
                                        </Button>
                                        <Button size="icon" variant="ghost" className="h-8 w-8 text-red-500 hover:text-red-600 hover:bg-red-50" onClick={cancelEditing}>
                                            <X className="h-4 w-4" />
                                        </Button>
                                    </div>
                                ) : (
                                    <div className="truncate group cursor-pointer" onClick={() => startEditing(task)}>
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="text-xs font-mono bg-purple-100 text-purple-700 px-2 py-0.5 rounded">
                                                #{task.id}
                                            </span>
                                            <h3 className={`font-medium text-lg leading-none truncate text-slate-900 ${
                                                task.completed ? 'line-through text-slate-400' : ''
                                            }`}>
                                                {task.title}
                                            </h3>
                                        </div>
                                        <p className="text-xs text-slate-600">
                                            {new Date(task.created_at).toLocaleDateString()}
                                        </p>
                                    </div>
                                )}
                            </div>
                          </div>

                          <div className="flex items-center w-full sm:w-auto justify-end">
                              {editingTaskId !== task.id && (
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="text-slate-400 hover:text-purple-600 hover:bg-purple-50 shrink-0 mr-1"
                                    onClick={() => startEditing(task)}
                                >
                                    <Edit2 className="h-4 w-4" />
                                </Button>
                              )}
                              <Button
                                variant="ghost"
                                size="icon"
                                className="text-slate-400 hover:text-red-600 hover:bg-red-50 shrink-0"
                                onClick={() => handleDeleteTask(task.id)}
                              >
                                <Trash2 className="h-5 w-5" />
                              </Button>
                          </div>
                       </CardContent>
                     </Card>
                   ))}
               </div>
            ) : (
                /* Clean Empty State */
                <Card className="border-dashed border-2 border-purple-200 bg-white/90 shadow-lg backdrop-blur-sm rounded-2xl">
                    <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                        <div className="bg-purple-50 p-4 rounded-full mb-4">
                            <CheckSquare className="h-12 w-12 text-purple-400" />
                        </div>
                        <h3 className="text-xl font-semibold mb-2 text-slate-900">No tasks found</h3>
                        <p className="text-slate-600 max-w-sm mx-auto mb-6">
                            {searchQuery ? "No tasks match your search." : "You don't have any tasks yet. Create one to get started!"}
                        </p>
                        {!searchQuery && (
                          <Button
                            variant="outline"
                            onClick={() => document.querySelector('input')?.focus()}
                          >
                            Create your first task
                          </Button>
                        )}
                    </CardContent>
                </Card>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
