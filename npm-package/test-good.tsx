/**
 * Well-structured React component
 */

interface UserProps {
  id: string;
  name: string;
  onUpdate: (data: User) => void;
}

export const UserCard: React.FC<UserProps> = ({ id, name, onUpdate }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const handleUpdate = async (newName: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/users/${id}`, {
        method: 'PUT',
        body: JSON.stringify({ name: newName }),
      });

      if (!response.ok) {
        throw new Error(`Failed to update user: ${response.statusText}`);
      }

      const data = await response.json();
      onUpdate(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setIsLoading(false);
    }
  };

  if (error) {
    return <div className="error">Error: {error.message}</div>;
  }

  return (
    <div className="card">
      <h2>{name}</h2>
      <button
        onClick={() => handleUpdate('Updated Name')}
        disabled={isLoading}
      >
        {isLoading ? 'Updating...' : 'Update'}
      </button>
    </div>
  );
};
