def append_channel_name_to_url(self, url, channel_name):
    """
    Appends the channel name to the URL as a parameter for debugging or tracking.
    Example: http://example.com → http://example.com?channel=Sport5_HD
    """
    try:
        if not url or not channel_name:
            return url

        clean_name = channel_name.strip().replace(" ", "_")
        if "?" in url:
            return f"{url}&channel={clean_name}"
        else:
            return f"{url}?channel={clean_name}"
    except Exception as e:
        print(f"[append_channel_name_to_url] Error: {e}")
        return url

    def getUrl(self, channel):
        """
        Extracts the URL from a channel string.
        """
        return channel.split(' (')[1].strip(')')


    def getUrlFromTextByChannelName(self, channel_name):
        lines = self.textEdit.toPlainText().splitlines()
        for i in range(len(lines) - 1):
            if lines[i].startswith("#EXTINF") and channel_name in lines[i]:
                url_line = lines[i + 1]
                if url_line.startswith("http"):
                    return url_line
        return ""

