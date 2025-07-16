import { writable } from 'svelte/store';

// Projects store
export const projects = writable<any[]>([]);

// Conversations store with update method
function createConversationsStore() {
	const { subscribe, set, update } = writable<any[]>([]);

	return {
		subscribe,
		set,
		update,
		updateConversation: (id: string, data: any) => {
			update(conversations => 
				conversations.map(conv => conv.id === id ? { ...conv, ...data } : conv)
			);
		}
	};
}

export const conversations = createConversationsStore();

// Connection status store
export const connectionStatus = writable<'connected' | 'disconnected'>('disconnected');