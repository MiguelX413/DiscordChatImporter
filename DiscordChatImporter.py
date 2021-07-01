#!/usr/bin/env python
from discord_webhook import DiscordWebhook, DiscordEmbed
from dateutil import parser

try:
    from progressbar import progressbar

    progressbarimport = True
except ModuleNotFoundError:
    progressbarimport = False

try:
    import ujson

    json = ujson
except ModuleNotFoundError:
    import json

import re

url_re = re.compile("\?size.*")


def main(filepath: str, url: str, bar: bool = True) -> None:
    usebar = bar and progressbarimport
    with open(filepath, "r") as f:
        filedata = json.loads(f.read())
    messages = filedata.get("messages")
    for message in progressbar(messages, redirect_stdout=True) if usebar else messages:
        timestamp, timestampEdited, isPinned, content, author, attachments, embeds = (
            message.get("timestamp"),
            message.get("timestampEdited"),
            message.get("isPinned"),
            message.get("content"),
            message.get("author"),
            message.get("attachments"),
            message.get("embeds"),
        )
        (
            author_id,
            author_name,
            author_nickname,
            author_color,
            author_is_bot,
            author_avatar_url,
        ) = (
            author.get("id"),
            author.get("name"),
            author.get("nickname"),
            author.get("color"),
            author.get("isBot"),
            author.get("avatarUrl"),
        )
        # print(url_re.sub("", author_avatar_url))
        webhook = DiscordWebhook(
            url=url,
            rate_limit_retry=True,
            username=author_name,
            avatar_url=url_re.sub("", author_avatar_url),
        )

        embed1 = DiscordEmbed()
        if author_color is not None:
            embed1.set_color(author_color.replace("#", ""))
        embed1.set_author(
            name=author_name,
            url="https://discordapp.com/users/" + author_id,
            icon_url=url_re.sub("", author_avatar_url),
        )
        embed1.add_embed_field(
            name="Discord User", value="<@%s>" % author_id, inline=True
        )
        embed1.add_embed_field(name="Name", value=author_name, inline=True)
        if (author_nickname != author_name) and (author_nickname != ""):
            embed1.add_embed_field(name="Nickname", value=author_nickname, inline=True)
        if author_is_bot:
            embed1.add_embed_field(name="isBot", value="True", inline=False)
        if isPinned:
            embed1.add_embed_field(
                name="isPinned", value="True", inline=True if author_is_bot else False
            )
        embed1.set_timestamp(parser.isoparse(timestamp).timestamp())
        webhook.add_embed(embed1)

        if (timestampEdited != None) and (timestampEdited != ""):
            embed2 = DiscordEmbed()
            if author_color is not None:
                embed2.set_color(author_color.replace("#", ""))
            embed2.set_timestamp(parser.isoparse(timestampEdited).timestamp())
            embed2.set_footer(text="Edited")
            webhook.add_embed(embed2)

        if content != "":
            embed3 = DiscordEmbed(
                # title="Content",
                description=content,
            )
            if author_color is not None:
                embed3.set_color(author_color.replace("#", ""))
            webhook.add_embed(embed3)

        for embed in embeds:
            (
                embed_title,
                embed_url,
                embed_timestamp,
                embed_description,
                embed_color,
                embed_thumbnail,
                embed_footer,
                embed_fields,
                embed_author,
            ) = (
                embed.get("title"),
                embed.get("url"),
                embed.get("timestamp"),
                embed.get("description"),
                embed.get("color"),
                embed.get("thumbnail"),
                embed.get("footer"),
                embed.get("fields"),
                embed.get("author"),
            )
            sub_embed = DiscordEmbed()
            if embed_title != "":
                sub_embed.set_title(embed_title)
            if (embed_url != "") and (embed_url != None):
                sub_embed.set_url(embed_url)
            if (embed_timestamp != "") and (embed_timestamp != None):
                sub_embed.set_timestamp(parser.isoparse(embed_timestamp).timestamp())
            if embed_description != "":
                sub_embed.set_description(embed_description)
            if embed_color is not None:
                sub_embed.set_color(embed_color.replace("#", ""))
            if embed_thumbnail is not None:
                sub_embed.set_thumbnail(
                    url=embed_thumbnail.get("url"),
                    width=embed_thumbnail.get("width"),
                    height=embed_thumbnail.get("height"),
                )
            if embed_footer is not None:
                sub_embed.set_footer(text=embed_footer.get("text"))
            if embed_fields is not None:
                for field in embed_fields:
                    sub_embed.add_embed_field(
                        name=field.get("name"),
                        value=field.get("value"),
                        inline=field.get("isInline"),
                    )
            webhook.add_embed(sub_embed)

        response = webhook.execute()
        print(response)


if __name__ == "__main__":
    import argparse

    argparser = argparse.ArgumentParser(
        description="Loads data produced with DiscordChatImporter"
    )
    argparser.add_argument("-f", "--file", help="JSON File", type=str, required=True)
    argparser.add_argument("-u", "--url", help="Webhook URL", type=str, required=True)
    args = argparser.parse_args()
    main(args.file, args.url)
