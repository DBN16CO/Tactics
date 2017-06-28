/**
 * Below are the basic implementations of the 2-Tuple and the 3-Tuple
 * With varied names to prevent namespace conflicts if Unity were to
 * ever catch up to modern .NET
 */
 // 2-Tuple
public class Twople<T,U>
{
    public T Item1 { get; private set; }
    public U Item2 { get; private set; }

    public Twople(T item1, U item2)
    {
        Item1 = item1;
        Item2 = item2;
    }
}

public static class Twople
{
    public static Twople<T, U> Create<T, U>(T item1, U item2)
    {
        return new Twople<T, U>(item1, item2);
    }
}

// 3-Tuple
public class Threeple<T,U,V>
{
    public T Item1 { get; private set; }
    public U Item2 { get; private set; }
    public V Item3 { get; private set; }

    public Threeple(T item1, U item2, V item3)
    {
        Item1 = item1;
        Item2 = item2;
        Item3 = item3;
    }
}

public static class Threeple
{
    public static Threeple<T, U, V> Create<T, U, V>(T item1, U item2, V item3)
    {
        return new Threeple<T, U, V>(item1, item2, item3);
    }
}