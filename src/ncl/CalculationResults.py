
class CalculationResults:
    
    def __init__(self, elapsed:float, status:str):
        
        if not isinstance(elapsed, (float, int)):
            raise TypeError("The elapsed time must be a Float or Integer")
        
        if not isinstance(status, str):
            raise TypeError("The status of the Calculation must be a string")
        
        self.elapsed = elapsed
        self.status = status
        
    def getCalculationTime(self):
        """Gets the Calculation time in Human Readable Clock Format

        ## Parameters : \n
            self - Default Parameter for the Class Instance \n

        ## Returns : \n
            str - The time in a clock format (x days : y hours : z mins : a sec)
        """
        # Convert Seconds to Hours, Minutes, and Seconds
        days = self.elapsed // 86400
        hours = (self.elapsed % 86400) // 3600
        minutes = (self.elapsed % 3600) // 60
        remainingSeconds = self.elapsed % 60

        # Generate the Time String
        parts = []
        if days > 0:
            parts.append(f"{int(days)} day{'s' if days > 1 else ''}")
        if hours > 0:
            parts.append(f"{int(hours)} hour{'s' if hours > 1 else ''}")
        if minutes > 0:
            parts.append(f"{int(minutes)} minute{'s' if minutes > 1 else ''}")
        if remainingSeconds > 0:
            parts.append(
                f"{int(remainingSeconds)} second{'s' if remainingSeconds > 1 else ''}"
            )

        # Return the Time String
        return ", ".join(parts) if parts else "0 seconds"
    