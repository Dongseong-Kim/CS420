#include "YourPolicy1.hpp"
#include "MemoryStructure.hpp"
#include "ScheduleProcessor.hpp"
#include "defines.hpp"
#include <thread>

int defragmentPolicy1End(int target_size);
int defragmentPolicy1Front(int target_size);

// Policy1 : Best Fit

void* YourPolicy1::onMalloc(int size)
{
	MemoryStructure* ms = MemoryStructure::getInstance();

	while (true)
	{
		void* prev_end = 0;
		void* min_end = 0;
		int min_frag_size = 0x7fffffff;

		for (int i = 0; i < ms->getAllocationListSize(); i++)
		{
			Allocation alloc = ms->getAllocation(i);
			int frag_size = (int)alloc.addr - (int)prev_end;
			if ( frag_size >= size && min_frag_size > frag_size)
			{
				min_frag_size = frag_size;
				min_end = prev_end;
			}

			prev_end = (void*)((int)alloc.addr + (int)alloc.size);
		}

		if (MAX_MEMORY_CAP - (int)prev_end >= size && min_frag_size > MAX_MEMORY_CAP - (int)prev_end)
		{
			min_frag_size = MAX_MEMORY_CAP - (int)prev_end;
			min_end = prev_end;
		}

		if (min_frag_size != 0x7fffffff)
		{
			ASSERT(ms->allocate(min_end, size));
			return min_end;
		}

		if (!defragmentPolicy1End(size)) defragmentPolicy1Front(size);
	}
}

void YourPolicy1::onFree(void* address)
{
	MemoryStructure* ms = MemoryStructure::getInstance();

	for (int i = 0; i < ms->getAllocationListSize(); i++)
	{
		Allocation alloc = ms->getAllocation(i);
		if (alloc.addr == address)
		{
			ASSERT(ms->deallocate(address));
			return;
		}
	}

	printf("DE Error : allocation not found! (%d, %p)\n", address, address);
	exit(1);
}

int defragmentPolicy1End(int target_size)
{
	printf("*** Fast defragmentation!! Target Size : %d\n", target_size);
	std::this_thread::sleep_for(std::chrono::milliseconds(300));
	MemoryStructure* ms = MemoryStructure::getInstance();
	int last_cap = MAX_MEMORY_CAP;

	// Retry until threshold
	for (int search_length = ms->getAllocationListSize(); search_length; search_length--)
	{
		// Move while moving allocation succeeds
		for (bool succeeded = true; succeeded;)
		{
			succeeded = false;
			Allocation alloc_from = ms->getAllocation(search_length - 1);
			void* prev_end = 0;
			// Search for the space to move on
			for (int i = 0; i < search_length; i++)
			{
				Allocation alloc_front_to = ms->getAllocation(i);
				// Found the space
				if ((int)alloc_front_to.addr - (int)prev_end >= alloc_from.size)
				{
					ScheduleProcessor::getInstance()->notifyAddressChange(alloc_from.addr, prev_end);
					// Move allocation
					ASSERT(ms->migrate(alloc_from.addr, prev_end));
					succeeded = true;
					break;
				}
				prev_end = (void*)((int)alloc_front_to.addr + alloc_front_to.size);
			}
			// Check if the space is enough
			Allocation last_alloc = ms->getAllocation(search_length - 1);
			if (last_cap - (int)last_alloc.addr - last_alloc.size >= target_size)
			{
				printf("good! %d at %d\n", search_length - 1, last_alloc.addr);
				return true;
			}
		}

		last_cap = (int)ms->getAllocation(search_length - 1).addr;
	}

	return false;
}


int defragmentPolicy1Front(int target_size)
{
	printf("*** Fast defragmentation failed. Slow defragmentation....\n");
	std::this_thread::sleep_for(std::chrono::milliseconds(300));
	MemoryStructure* ms = MemoryStructure::getInstance();
	void* prev_end = 0;

	for (int i = 0; i < ms->getAllocationListSize(); i++)
	{
		Allocation alloc_from = ms->getAllocation(i);
		int rem_space = (int)alloc_from.addr - (int)prev_end;
		if (rem_space > 0)
		{
			if (rem_space >= target_size) return 1;
			ScheduleProcessor::getInstance()->notifyAddressChange(alloc_from.addr, prev_end);
			// Move allocation
			ASSERT(ms->migrate(alloc_from.addr, prev_end));
		}
		prev_end = (void*)((int)prev_end + alloc_from.size);
	}

	return 0;
}