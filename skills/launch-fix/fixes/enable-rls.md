# enable-rls (guided)
Supabase/Postgres: for each table in `public` add a migration:
`alter table X enable row level security;` then policies, e.g. `create policy "own rows" on X for select using (auth.uid() = user_id);` and matching insert/update/delete policies with `with check`. Test with the anon key that user A cannot read user B's rows. Firebase: write rules that compare `request.auth.uid` to the document owner; never `if true`. Show each policy to the owner: wrong policies silently lock users out or leak data.
