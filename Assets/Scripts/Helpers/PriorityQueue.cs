using System.Collections.Generic;
using System.Linq;
/*
 * Implementation of Priority Queue for C#, because C# is poop and does not have one.
 *
 * Idea to further improve: Implement red-black tree to mimic SortedSet use that to track max which
 * would make implementation slightly better as Dictionary lookups (which happen every time)
 * would then be O(1), rather than O(logN), and the occasional insert / delete for new priorites
 * which would be O(logN) would not be as often.
 */
public class PriorityQueue<V>{
	private SortedDictionary<int, Queue<V> > _queue;
	private int _count;

#region Setters and Getters
	public int Count {
		get{return _count;}
	}
#endregion

	// Default constructor, initialize  queue, reset count
	public PriorityQueue(){
		_queue = new SortedDictionary<int, Queue<V> >();
		_count = 0;
	}

	// Enqueue into the proper queue of the dictionary (whose key is the priority)
	public void Enqueue(int priority, V value){
		Queue<V> thisQueue;
		bool getValueSuccess = _queue.TryGetValue(priority, out thisQueue);

		if(!getValueSuccess){
			thisQueue = new Queue<V>();
			_queue.Add(priority, thisQueue);
		}

		thisQueue.Enqueue(value);
		_count++;
	}

	// Dequeue from the highest queue in the dictionary
	public V Dequeue(){
		int highestPriority = _queue.Keys.Max();

		Queue<V> thisQueue;
		_queue.TryGetValue(highestPriority, out thisQueue);

		V returnValue = thisQueue.Dequeue();

		if(thisQueue.Count == 0){
			_queue.Remove(highestPriority);
		}

		_count--;

		return returnValue;
	}

}