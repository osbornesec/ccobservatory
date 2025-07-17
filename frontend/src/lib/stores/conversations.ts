import { writable, derived } from 'svelte/store';
import type { Project, Conversation } from '$lib/types';

// Projects store with additional methods
function createProjectsStore() {
	const { subscribe, set, update } = writable<Project[]>([]);

	return {
		subscribe,
		set,
		update,
		addProject: (project: Project) => {
			update(projects => [...projects, project]);
		},
		clear: () => {
			set([]);
		}
	};
}

export const projects = createProjectsStore();

// Conversations store with update method
function createConversationsStore() {
	const { subscribe, set, update } = writable<Conversation[]>([]);

	return {
		subscribe,
		set,
		update,
		updateConversation: (id: string, data: Partial<Conversation>) => {
			update(conversations => 
				conversations.map(conv => conv.id === id ? { ...conv, ...data } : conv)
			);
		},
		addConversation: (conversation: Conversation) => {
			update(conversations => [...conversations, conversation]);
		},
		removeConversation: (id: string) => {
			update(conversations => conversations.filter(conv => conv.id !== id));
		},
		clear: () => {
			set([]);
		}
	};
}

export const conversationsStore = createConversationsStore();

// Legacy export for backward compatibility
export const conversations = conversationsStore;

// Active conversation store
export const activeConversation = writable<Conversation | null>(null);

// Messages store
export const messages = writable<any[]>([]);

// Active project store
export const activeProject = writable<Project | null>(null);

// Search store
export const search = writable<string>('');

// Derived stores
export const filteredConversations = derived(
	[conversationsStore, search],
	([$conversations, $search]) => {
		if (!$search) return $conversations;
		return $conversations.filter(conv => 
			conv.title.toLowerCase().includes($search.toLowerCase()) ||
			conv.summary?.toLowerCase().includes($search.toLowerCase())
		);
	}
);

export const conversationStats = derived(
	conversationsStore,
	($conversations) => ({
		total: $conversations.length,
		active: $conversations.filter(c => c.status === 'active').length,
		completed: $conversations.filter(c => c.status === 'completed').length,
		error: $conversations.filter(c => c.status === 'error').length
	})
);

// Connection status store with additional states and methods
function createConnectionStore() {
	const { subscribe, set } = writable<'connected' | 'disconnected' | 'connecting' | 'error'>('disconnected');

	return {
		subscribe,
		set,
		connecting: () => set('connecting'),
		connected: () => set('connected'),
		disconnected: () => set('disconnected'),
		error: () => set('error')
	};
}

export const connectionStatus = createConnectionStore();